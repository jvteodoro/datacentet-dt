DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'event_log_stream_id_version_counter_key'
    ) THEN
        ALTER TABLE event_log
            ADD CONSTRAINT event_log_stream_id_version_counter_key UNIQUE (stream_id, version_counter);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'event_log_stream_id_ingest_id_key'
    ) THEN
        ALTER TABLE event_log
            ADD CONSTRAINT event_log_stream_id_ingest_id_key UNIQUE (stream_id, ingest_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_event_log_stream_seq
    ON event_log(stream_id, seq);

CREATE INDEX IF NOT EXISTS idx_event_log_stream_version
    ON event_log(stream_id, version_counter);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'snapshot_store_stream_id_version_counter_key'
    ) THEN
        ALTER TABLE snapshot_store
            ADD CONSTRAINT snapshot_store_stream_id_version_counter_key UNIQUE (stream_id, version_counter);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_snapshot_latest
    ON snapshot_store(stream_id, version_counter DESC);
