-- Stage 8 Schema Update: Add function for BM25 indexing
-- Run this in your Supabase SQL Editor or execute via API

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