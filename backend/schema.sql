-- Enable pgvector extension
create extension if not exists vector;

-- Create documents table
create table if not exists documents (
  id uuid default gen_random_uuid() primary key,
  owner_id text not null,
  title text not null,
  type text not null,
  metadata jsonb default '{}',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create document_sections table (with contextual retrieval support)
create table if not exists document_sections (
  id uuid default gen_random_uuid() primary key,
  document_id uuid references documents(id) on delete cascade not null,
  content text not null,
  contextual_content text, -- Contextual description for enhanced retrieval
  is_contextualized boolean default false, -- Whether chunk has been enhanced
  embedding vector(1536), -- OpenAI text-embedding-3-small dimension
  metadata jsonb default '{}',
  contextual_metadata jsonb default '{}', -- Metadata for contextual processing
  chunk_index integer not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes for better performance
create index if not exists document_sections_document_id_idx on document_sections(document_id);
create index if not exists document_sections_embedding_idx on document_sections using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists document_sections_contextualized_idx on document_sections(is_contextualized);
create index if not exists document_sections_contextual_metadata_idx on document_sections using gin (contextual_metadata);

-- Create contextual processing statistics table
create table if not exists contextual_processing_stats (
  id uuid default gen_random_uuid() primary key,
  document_id uuid references documents(id) on delete cascade,
  owner_id text not null,
  total_chunks integer not null,
  processed_chunks integer not null,
  failed_chunks integer not null,
  total_tokens_used integer default 0,
  processing_time_seconds float default 0,
  cost_estimate_usd decimal(10,4) default 0,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security
alter table documents enable row level security;
alter table document_sections enable row level security;
alter table contextual_processing_stats enable row level security;

-- RLS Policies for documents table
create policy "Users can view their own documents"
  on documents for select
  using (owner_id = current_setting('app.current_user_id')::text);

create policy "Users can insert their own documents"
  on documents for insert
  with check (owner_id = current_setting('app.current_user_id')::text);

create policy "Users can update their own documents"
  on documents for update
  using (owner_id = current_setting('app.current_user_id')::text);

create policy "Users can delete their own documents"
  on documents for delete
  using (owner_id = current_setting('app.current_user_id')::text);

-- RLS Policies for document_sections table
create policy "Users can view sections of their documents"
  on document_sections for select
  using (
    document_id in (
      select id from documents 
      where owner_id = current_setting('app.current_user_id')::text
    )
  );

create policy "Users can insert sections for their documents"
  on document_sections for insert
  with check (
    document_id in (
      select id from documents 
      where owner_id = current_setting('app.current_user_id')::text
    )
  );

create policy "Users can update sections of their documents"
  on document_sections for update
  using (
    document_id in (
      select id from documents 
      where owner_id = current_setting('app.current_user_id')::text
    )
  );

create policy "Users can delete sections of their documents"
  on document_sections for delete
  using (
    document_id in (
      select id from documents 
      where owner_id = current_setting('app.current_user_id')::text
    )
  );

-- RLS Policies for contextual_processing_stats table
create policy "Users can view their own processing stats"
  on contextual_processing_stats for select
  using (owner_id = current_setting('app.current_user_id')::text);

create policy "Users can insert their own processing stats"
  on contextual_processing_stats for insert
  with check (owner_id = current_setting('app.current_user_id')::text);

-- Function to update updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = timezone('utc'::text, now());
  return new;
end;
$$ language plpgsql;

-- Trigger to automatically update updated_at
create trigger update_documents_updated_at
  before update on documents
  for each row
  execute function update_updated_at_column();

-- Function for vector similarity search with permissions
create or replace function search_document_sections(
  query_embedding vector(1536),
  owner_id text,
  match_threshold float default 0.7,
  match_count int default 5
)
returns table(
  id uuid,
  document_id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    ds.id,
    ds.document_id,
    ds.content,
    ds.metadata,
    1 - (ds.embedding <=> query_embedding) as similarity
  from document_sections ds
  inner join documents d on d.id = ds.document_id
  where d.owner_id = search_document_sections.owner_id
    and ds.embedding is not null
    and 1 - (ds.embedding <=> query_embedding) > match_threshold
  order by ds.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Function to get all document sections for a user (for BM25 indexing)
create or replace function get_user_document_sections(
  user_id text
)
returns table(
  id uuid,
  document_id uuid,
  content text,
  chunk_index integer
)
language plpgsql
as $$
begin
  return query
  select
    ds.id,
    ds.document_id,
    ds.content,
    ds.chunk_index
  from document_sections ds
  inner join documents d on d.id = ds.document_id
  where d.owner_id = user_id
  order by ds.document_id, ds.chunk_index;
end;
$$;

-- Enhanced function for contextual retrieval search
create or replace function search_document_sections_contextual(
  query_embedding vector(1536),
  owner_id text,
  match_threshold float default 0.7,
  match_count int default 5,
  prefer_contextual boolean default true
)
returns table(
  id uuid,
  document_id uuid,
  content text,
  contextual_content text,
  metadata jsonb,
  similarity float,
  is_contextualized boolean
)
language plpgsql
as $$
begin
  return query
  select
    ds.id,
    ds.document_id,
    ds.content,
    ds.contextual_content,
    ds.metadata,
    1 - (ds.embedding <=> query_embedding) as similarity,
    ds.is_contextualized
  from document_sections ds
  inner join documents d on d.id = ds.document_id
  where d.owner_id = search_document_sections_contextual.owner_id
    and ds.embedding is not null
    and 1 - (ds.embedding <=> query_embedding) > match_threshold
    and (
      case 
        when prefer_contextual then 
          (ds.is_contextualized = true or 
           not exists (
             select 1 from document_sections ds2 
             where ds2.document_id = ds.document_id 
             and ds2.is_contextualized = true
           ))
        else true
      end
    )
  order by 
    case when prefer_contextual then ds.is_contextualized::int else 0 end desc,
    ds.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Function to get contextual content for BM25 indexing
create or replace function get_user_document_sections_contextual(
  user_id text,
  prefer_contextual boolean default true
)
returns table(
  id uuid,
  document_id uuid,
  content text,
  contextual_content text,
  chunk_index integer,
  is_contextualized boolean
)
language plpgsql
as $$
begin
  return query
  select
    ds.id,
    ds.document_id,
    ds.content,
    ds.contextual_content,
    ds.chunk_index,
    ds.is_contextualized
  from document_sections ds
  inner join documents d on d.id = ds.document_id
  where d.owner_id = user_id
  order by ds.document_id, ds.chunk_index;
end;
$$;

-- Function to get contextual processing statistics
create or replace function get_contextual_processing_stats(
  user_id text,
  days_back integer default 30
)
returns table(
  total_documents integer,
  total_chunks integer,
  total_tokens integer,
  estimated_cost_usd decimal
)
language plpgsql
as $$
begin
  return query
  select
    count(distinct cps.document_id)::integer,
    sum(cps.total_chunks)::integer,
    sum(cps.total_tokens_used)::integer,
    sum(cps.cost_estimate_usd)
  from contextual_processing_stats cps
  where cps.owner_id = user_id
    and cps.created_at >= (now() - interval '1 day' * days_back);
end;
$$;