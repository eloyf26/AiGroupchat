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

-- Create document_sections table
create table if not exists document_sections (
  id uuid default gen_random_uuid() primary key,
  document_id uuid references documents(id) on delete cascade not null,
  content text not null,
  embedding vector(1536), -- OpenAI text-embedding-3-small dimension
  metadata jsonb default '{}',
  chunk_index integer not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes for better performance
create index if not exists document_sections_document_id_idx on document_sections(document_id);
create index if not exists document_sections_embedding_idx on document_sections using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- Enable Row Level Security
alter table documents enable row level security;
alter table document_sections enable row level security;

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