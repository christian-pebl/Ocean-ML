-- Ocean-ML Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    thumbnail_path TEXT,
    duration_seconds INTEGER,
    frame_count INTEGER,
    resolution TEXT,
    fps FLOAT,
    file_size_bytes BIGINT,
    uploaded_by UUID REFERENCES auth.users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Annotation status
    annotated BOOLEAN DEFAULT FALSE,
    annotated_by UUID REFERENCES auth.users(id),
    annotated_at TIMESTAMP WITH TIME ZONE,
    annotation_storage_path TEXT,
    detection_count INTEGER DEFAULT 0,

    -- Locking mechanism
    locked_by UUID REFERENCES auth.users(id),
    locked_at TIMESTAMP WITH TIME ZONE,
    lock_expires_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Annotations table
CREATE TABLE annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    annotated_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    frames_annotated INTEGER,
    detection_count INTEGER,
    species_counts JSONB,
    annotation_format TEXT DEFAULT 'yolo',
    storage_path TEXT NOT NULL,

    UNIQUE(video_id)
);

-- Training runs table
CREATE TABLE training_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    started_by UUID REFERENCES auth.users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Configuration
    model_type TEXT NOT NULL,
    epochs INTEGER NOT NULL,
    dataset_id TEXT NOT NULL,
    video_ids UUID[],

    -- Results
    status TEXT DEFAULT 'pending',
    modal_call_id TEXT,
    map50 FLOAT,
    map50_95 FLOAT,
    precision FLOAT,
    recall FLOAT,
    final_loss FLOAT,
    current_epoch INTEGER DEFAULT 0,
    current_loss FLOAT,
    current_map FLOAT,

    -- Resource usage
    gpu_type TEXT,
    training_time_seconds INTEGER,
    cost_usd FLOAT,

    -- Model storage
    model_storage_path TEXT,
    logs_storage_path TEXT
);

-- Inference runs table
CREATE TABLE inference_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    started_by UUID REFERENCES auth.users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    video_id UUID REFERENCES videos(id),
    model_id UUID REFERENCES training_runs(id),

    status TEXT DEFAULT 'pending',
    modal_call_id TEXT,

    detection_count INTEGER,
    average_confidence FLOAT,
    results_storage_path TEXT,
    annotated_video_path TEXT,

    processing_time_seconds INTEGER,
    cost_usd FLOAT
);

-- Activity log table
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    action_type TEXT NOT NULL,
    resource_type TEXT,
    resource_id UUID,
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX idx_videos_annotated ON videos(annotated);
CREATE INDEX idx_videos_uploaded_by ON videos(uploaded_by);
CREATE INDEX idx_videos_locked_by ON videos(locked_by);
CREATE INDEX idx_training_runs_status ON training_runs(status);
CREATE INDEX idx_training_runs_started_by ON training_runs(started_by);
CREATE INDEX idx_activity_log_timestamp ON activity_log(timestamp DESC);
CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_annotations_updated_at BEFORE UPDATE ON annotations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE annotations ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE inference_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies for videos table
CREATE POLICY "Users can view all videos"
    ON videos FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own videos"
    ON videos FOR INSERT
    WITH CHECK (auth.uid() = uploaded_by);

CREATE POLICY "Users can update videos they uploaded"
    ON videos FOR UPDATE
    USING (auth.uid() = uploaded_by);

CREATE POLICY "Users can delete their own videos"
    ON videos FOR DELETE
    USING (auth.uid() = uploaded_by);

-- RLS Policies for annotations table
CREATE POLICY "Users can view all annotations"
    ON annotations FOR SELECT
    USING (true);

CREATE POLICY "Users can insert annotations"
    ON annotations FOR INSERT
    WITH CHECK (auth.uid() = annotated_by);

CREATE POLICY "Users can update their own annotations"
    ON annotations FOR UPDATE
    USING (auth.uid() = annotated_by);

-- RLS Policies for training_runs table
CREATE POLICY "Users can view all training runs"
    ON training_runs FOR SELECT
    USING (true);

CREATE POLICY "Users can insert training runs"
    ON training_runs FOR INSERT
    WITH CHECK (auth.uid() = started_by);

CREATE POLICY "Users can update their own training runs"
    ON training_runs FOR UPDATE
    USING (auth.uid() = started_by);

-- RLS Policies for inference_runs table
CREATE POLICY "Users can view all inference runs"
    ON inference_runs FOR SELECT
    USING (true);

CREATE POLICY "Users can insert inference runs"
    ON inference_runs FOR INSERT
    WITH CHECK (auth.uid() = started_by);

-- RLS Policies for activity_log table
CREATE POLICY "Users can view all activity"
    ON activity_log FOR SELECT
    USING (true);

CREATE POLICY "Users can insert activity"
    ON activity_log FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create function to log activity
CREATE OR REPLACE FUNCTION log_activity(
    p_action_type TEXT,
    p_resource_type TEXT,
    p_resource_id UUID,
    p_metadata JSONB DEFAULT '{}'::JSONB
)
RETURNS UUID AS $$
DECLARE
    activity_id UUID;
BEGIN
    INSERT INTO activity_log (user_id, action_type, resource_type, resource_id, metadata)
    VALUES (auth.uid(), p_action_type, p_resource_type, p_resource_id, p_metadata)
    RETURNING id INTO activity_id;

    RETURN activity_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check and release expired locks
CREATE OR REPLACE FUNCTION release_expired_locks()
RETURNS INTEGER AS $$
DECLARE
    released_count INTEGER;
BEGIN
    UPDATE videos
    SET locked_by = NULL,
        locked_at = NULL,
        lock_expires_at = NULL
    WHERE lock_expires_at < NOW()
    AND locked_by IS NOT NULL;

    GET DIAGNOSTICS released_count = ROW_COUNT;
    RETURN released_count;
END;
$$ LANGUAGE plpgsql;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database schema created successfully!';
    RAISE NOTICE '📊 Tables: videos, annotations, training_runs, inference_runs, activity_log';
    RAISE NOTICE '🔒 Row Level Security enabled';
    RAISE NOTICE '📈 Indexes created for performance';
END $$;
