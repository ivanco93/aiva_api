-- Migration: create_cameras
-- Module: Camera

CREATE TABLE cameras (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name varchar(100) NOT NULL,
  code varchar(30) NOT NULL,
  location_id integer NOT NULL,
  source_type varchar(20) NOT NULL,
  source_url varchar(2048) NOT NULL,
  status varchar(20) NOT NULL DEFAULT 'active',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NULL,
  CONSTRAINT chk_cameras_location_id CHECK (location_id >= 0),
  CONSTRAINT chk_cameras_source_type CHECK (source_type IN ('rtsp', 'rtmp', 'http', 'hls', 'file')),
  CONSTRAINT chk_cameras_status CHECK (status IN ('active', 'inactive', 'maintenance'))
);

-- Único sin distinguir mayúsculas: 'CAM-001' y 'cam-001' son el mismo código.
CREATE UNIQUE INDEX uq_cameras_code ON cameras (lower(code));
CREATE INDEX idx_cameras_location ON cameras (location_id);
CREATE INDEX idx_cameras_status ON cameras (status);

COMMENT ON COLUMN cameras.code IS 'Código de negocio, ej. CAM-001';
COMMENT ON COLUMN cameras.source_type IS 'rtsp | rtmp | http | hls | file';
COMMENT ON COLUMN cameras.status IS 'active | inactive | maintenance';

-- Equivalente a ON UPDATE CURRENT_TIMESTAMP de MySQL. CREATE OR REPLACE permite
-- que otros módulos declaren la misma función sin depender de este.
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_cameras_updated_at
  BEFORE UPDATE ON cameras
  FOR EACH ROW
  WHEN (OLD.* IS DISTINCT FROM NEW.*)
  EXECUTE FUNCTION set_updated_at();
