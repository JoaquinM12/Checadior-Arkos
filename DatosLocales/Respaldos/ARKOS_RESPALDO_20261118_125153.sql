-- ==================================================
-- ARKOS CHECADOR - RESPALDO DE BASE DE DATOS
-- Fecha: 2026-11-18 12:51:53.707861
-- Base de datos: arkos
-- ==================================================

SET FOREIGN_KEY_CHECKS=0;


-- Tabla: tblclasesimpartidas
DROP TABLE IF EXISTS `tblclasesimpartidas`;
CREATE TABLE `tblclasesimpartidas` (
  `id_clase` int NOT NULL AUTO_INCREMENT,
  `id_maestro` int NOT NULL,
  `id_horario` int NOT NULL,
  `fecha` datetime NOT NULL,
  `hora_asistencia` datetime DEFAULT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `observaciones` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_clase`),
  KEY `FK_tblClasesImpartidas_tblHorarios` (`id_horario`),
  KEY `IX_tblClases_fecha` (`fecha`),
  KEY `IX_tblClases_maestro` (`id_maestro`),
  CONSTRAINT `FK_tblClasesImpartidas_tblHorarios` FOREIGN KEY (`id_horario`) REFERENCES `tblhorarios` (`id_horario`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_tblClasesImpartidas_tblMaestros` FOREIGN KEY (`id_maestro`) REFERENCES `tblmaestros` (`id_maestro`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `CK_tblClasesImpartidas_estado` CHECK ((`estado` in (_utf8mb4'ASISTENCIA',_utf8mb4'RETARDO')))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tblclasesimpartidas` (`id_clase`, `id_maestro`, `id_horario`, `fecha`, `hora_asistencia`, `estado`, `observaciones`, `fecha_registro`) VALUES (1, 1, 2, CONVERT(0x323032362d31312d31322031313a35383a3036 USING utf8mb4), CONVERT(0x323032362d31312d31322031313a35383a3036 USING utf8mb4), CONVERT(0x4153495354454e434941 USING utf8mb4), CONVERT(0x54656d617320696d7061727469646f733a0a6578616d656e USING utf8mb4), CONVERT(0x323032362d31312d31322031313a35383a3533 USING utf8mb4));


-- Tabla: tblfaltas
DROP TABLE IF EXISTS `tblfaltas`;
CREATE TABLE `tblfaltas` (
  `id_falta` int NOT NULL AUTO_INCREMENT,
  `id_maestro` int NOT NULL,
  `id_horario` int NOT NULL,
  `fecha` datetime NOT NULL,
  `tipo` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `maestro_cubrio` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observaciones` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_falta`),
  KEY `FK_tblFaltas_tblHorarios` (`id_horario`),
  KEY `IX_tblFaltas_fecha` (`fecha`),
  KEY `IX_tblFaltas_maestro` (`id_maestro`),
  CONSTRAINT `FK_tblFaltas_tblHorarios` FOREIGN KEY (`id_horario`) REFERENCES `tblhorarios` (`id_horario`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_tblFaltas_tblMaestros` FOREIGN KEY (`id_maestro`) REFERENCES `tblmaestros` (`id_maestro`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `CK_tblFaltas_tipo` CHECK ((`tipo` in (_utf8mb4'FALTA',_utf8mb4'JUSTIFICADA')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- Tabla: tblhorarios
DROP TABLE IF EXISTS `tblhorarios`;
CREATE TABLE `tblhorarios` (
  `id_horario` int NOT NULL AUTO_INCREMENT,
  `id_maestro` int NOT NULL,
  `id_materia` int NOT NULL,
  `dia` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL,
  `turno` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'VESPERTINO',
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ACTIVO',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_horario`),
  KEY `IX_tblHorarios_maestro` (`id_maestro`),
  KEY `IX_tblHorarios_materia` (`id_materia`),
  CONSTRAINT `FK_tblHorarios_tblMaestros` FOREIGN KEY (`id_maestro`) REFERENCES `tblmaestros` (`id_maestro`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_tblHorarios_tblMaterias` FOREIGN KEY (`id_materia`) REFERENCES `tblmaterias` (`id_materia`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `CK_tblHorarios_horas` CHECK ((`hora_fin` > `hora_inicio`))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tblhorarios` (`id_horario`, `id_maestro`, `id_materia`, `dia`, `hora_inicio`, `hora_fin`, `turno`, `estado`, `fecha_registro`) VALUES (1, 1, 3, CONVERT(0x4c554e4553 USING utf8mb4), CONVERT(0x31373a30303a3030 USING utf8mb4), CONVERT(0x31393a30303a3030 USING utf8mb4), CONVERT(0x56455350455254494e4f USING utf8mb4), CONVERT(0x41435449564f USING utf8mb4), CONVERT(0x323032362d31312d31322031313a31353a3132 USING utf8mb4));
INSERT INTO `tblhorarios` (`id_horario`, `id_maestro`, `id_materia`, `dia`, `hora_inicio`, `hora_fin`, `turno`, `estado`, `fecha_registro`) VALUES (2, 1, 2, CONVERT(0x4a5545564553 USING utf8mb4), CONVERT(0x31323a30303a3030 USING utf8mb4), CONVERT(0x31393a30303a3030 USING utf8mb4), CONVERT(0x56455350455254494e4f USING utf8mb4), CONVERT(0x41435449564f USING utf8mb4), CONVERT(0x323032362d31312d31322031313a35353a3038 USING utf8mb4));


-- Tabla: tblmaestros
DROP TABLE IF EXISTS `tblmaestros`;
CREATE TABLE `tblmaestros` (
  `id_maestro` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ACTIVO',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_maestro`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tblmaestros` (`id_maestro`, `nombre`, `apellido`, `estado`, `fecha_registro`) VALUES (1, CONVERT(0x4a6f617175696e204d617274696e USING utf8mb4), CONVERT(0x487565727461204c656f6e USING utf8mb4), CONVERT(0x41435449564f USING utf8mb4), CONVERT(0x323032362d31312d31312031343a31303a3235 USING utf8mb4));


-- Tabla: tblmaterias
DROP TABLE IF EXISTS `tblmaterias`;
CREATE TABLE `tblmaterias` (
  `id_materia` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `carrera` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cuatrimestre` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ACTIVA',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_materia`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tblmaterias` (`id_materia`, `nombre`, `carrera`, `cuatrimestre`, `estado`, `fecha_registro`) VALUES (1, CONVERT(0x4445524543484f20434956494c USING utf8mb4), CONVERT(0x4c444552 USING utf8mb4), CONVERT(0x5445524345524f USING utf8mb4), CONVERT(0x414354495641 USING utf8mb4), CONVERT(0x323032362d31312d31322031313a30373a3531 USING utf8mb4));
INSERT INTO `tblmaterias` (`id_materia`, `nombre`, `carrera`, `cuatrimestre`, `estado`, `fecha_registro`) VALUES (2, CONVERT(0x61646d696e697374726163696f6e2049 USING utf8mb4), CONVERT(0x4c414554 USING utf8mb4), CONVERT(0x5052494d45524f USING utf8mb4), CONVERT(0x414354495641 USING utf8mb4), CONVERT(0x323032362d31312d31322031313a31333a3533 USING utf8mb4));
INSERT INTO `tblmaterias` (`id_materia`, `nombre`, `carrera`, `cuatrimestre`, `estado`, `fecha_registro`) VALUES (3, CONVERT(0x636f6e746162696c696461642049 USING utf8mb4), CONVERT(0x4c434f4e USING utf8mb4), CONVERT(0x5155494e544f USING utf8mb4), CONVERT(0x414354495641 USING utf8mb4), CONVERT(0x323032362d31312d31322031313a31343a3035 USING utf8mb4));


SET FOREIGN_KEY_CHECKS=1;
