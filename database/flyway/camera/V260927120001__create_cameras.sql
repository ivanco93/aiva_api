-- Migration: create_cameras
-- Module: Camera

CREATE TABLE `cameras` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Código de negocio, ej. CAM-001',
  `location_id` int unsigned NOT NULL,
  `source_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'rtsp | rtmp | http | hls | file',
  `source_url` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT 'active | inactive | maintenance',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_cameras_code` (`code`),
  KEY `idx_cameras_location` (`location_id`),
  KEY `idx_cameras_status` (`status`),
  CONSTRAINT `chk_cameras_source_type` CHECK (`source_type` IN ('rtsp', 'rtmp', 'http', 'hls', 'file')),
  CONSTRAINT `chk_cameras_status` CHECK (`status` IN ('active', 'inactive', 'maintenance'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
