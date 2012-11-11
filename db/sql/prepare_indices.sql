-- Indices required for a more efficient built-up of the hiking database.

CREATE INDEX relation_member_idx ON relation_members USING btree (member_id, member_type);
CREATE INDEX idx_nodes_tags ON nodes USING GIN(tags);
CREATE INDEX idx_ways_tags ON ways USING GIN(tags);
CREATE INDEX idx_relations_tags ON relations USING GIN(tags);

ANALYSE;

CREATE EXTENSION pg_trgm;
