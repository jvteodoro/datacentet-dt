CREATE TABLE IF NOT EXISTS event_log (
    seq BIGSERIAL PRIMARY KEY,
    stream_id TEXT NOT NULL,
    version_counter BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    payload_sha256 BYTEA NOT NULL,
    ingest_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (stream_id, ingest_id)
);

CREATE INDEX IF NOT EXISTS idx_event_log_stream_seq
    ON event_log(stream_id, seq);

CREATE INDEX IF NOT EXISTS idx_event_log_stream_version_counter
    ON event_log(stream_id, version_counter);

CREATE INDEX IF NOT EXISTS idx_event_log_event_type
    ON event_log(event_type);

CREATE TABLE IF NOT EXISTS snapshot_store (
    snapshot_id BIGSERIAL PRIMARY KEY,
    stream_id TEXT NOT NULL,
    version_counter BIGINT NOT NULL,
    snapshot_payload BYTEA NOT NULL,
    snapshot_sha256 BYTEA NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (stream_id, version_counter)
);

CREATE INDEX IF NOT EXISTS idx_snapshot_store_stream_version_desc
    ON snapshot_store(stream_id, version_counter DESC);
