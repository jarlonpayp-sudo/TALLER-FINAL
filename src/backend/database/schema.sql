
-- Base de Datos: allquality_db
-- Proyecto: Sistema de Gestión Comercial de Repuestos para Motocicletas
-- Asignatura: Ingeniería de Software II - COTECNOVA 2026-2
-- Motor: MySQL 8.0+ / MariaDB (InnoDB)

CREATE DATABASE IF NOT EXISTS allquality_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE allquality_db;

-- 1. Tabla de Roles
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rol_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_roles FOREIGN KEY (rol_id) REFERENCES roles(id) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 3. Tabla de Categorías de Repuestos
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Tabla de Repuestos y Accesorios
CREATE TABLE IF NOT EXISTS repuestos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT NOT NULL,
    codigo_referencia VARCHAR(50) NOT NULL UNIQUE,
    codigo_oem VARCHAR(50),
    nombre VARCHAR(150) NOT NULL,
    marca_moto VARCHAR(80),
    precio_compra DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    precio_venta DECIMAL(12,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 3,
    activo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_repuestos_categorias FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON UPDATE CASCADE,
    CONSTRAINT chk_precio_venta CHECK (precio_venta > 0),
    CONSTRAINT chk_stock_actual CHECK (stock_actual >= 0),
    CONSTRAINT chk_stock_minimo CHECK (stock_minimo >= 0)
) ENGINE=InnoDB;

-- 5. Tabla de Ventas (Cabecera)
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    numero_factura VARCHAR(50) NOT NULL UNIQUE,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    iva DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    estado VARCHAR(20) NOT NULL DEFAULT 'COMPLETADA', -- COMPLETADA, ANULADA
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ventas_usuarios FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- 6. Tabla de Detalle de Venta
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    repuesto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_detalles_ventas FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    CONSTRAINT fk_detalles_repuestos FOREIGN KEY (repuesto_id) REFERENCES repuestos(id),
    CONSTRAINT chk_cantidad CHECK (cantidad > 0)
) ENGINE=InnoDB;

-- 7. Tabla de Auditoría de Movimientos de Inventario
CREATE TABLE IF NOT EXISTS auditoria_movimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repuesto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    tipo_movimiento VARCHAR(30) NOT NULL, -- VENTA, COMPRA, ANULACION, AJUSTE
    cantidad INT NOT NULL,
    stock_anterior INT NOT NULL,
    stock_nuevo INT NOT NULL,
    justificacion VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_repuestos FOREIGN KEY (repuesto_id) REFERENCES repuestos(id),
    CONSTRAINT fk_auditoria_usuarios FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (id, nombre, descripcion) VALUES
(1, 'ADMIN', 'Administrador del sistema con control total'),
(2, 'VENDEDOR', 'Personal de mostrador para ventas y consulta de precios'),
(3, 'INVENTARIO', 'Encargado de recepción de mercancía y ajustes de bodega');

-- Contraseña por defecto: Admin123* (hash SHA-256 / Pbkdf2)
INSERT IGNORE INTO usuarios (id, rol_id, nombre, email, password_hash, activo) VALUES
(1, 1, 'Alejandro Londoño', 'admin@allquality.com', 'pbkdf2:sha256:1000000$SSDmAem1zvm5BJlR$ef3fd42b108d997c03970069576a7e675685ed71853f2984aa81f65cdeeac4b1', 1),
(2, 2, 'Cristian Carabalí', 'vendedor@allquality.com', 'pbkdf2:sha256:1000000$GL9QXf8uwKPxWPhM$6ef23813eba1d98c5a09f14d65c0b557ec1133582846a621e5babec3047e271c', 1),
(3, 3, 'Steven Rendón', 'bodega@allquality.com', 'pbkdf2:sha256:1000000$Y83sSRiXGebBJGgk$bf15d53bcc456f364e00b5f3bf8222008b2cb9e15fb1ee6e876bf2b5ffa98d51', 1);

INSERT IGNORE INTO categorias (id, nombre, descripcion) VALUES
(1, 'Frenos', 'Pastillas, bandas, discos, bombas y líquidos de freno'),
(2, 'Motor y Transmisión', 'Kits de arrastre, piñones, coronas, cadenas y cilindros'),
(3, 'Eléctrico', 'Bujías, bobinas, reguladores, baterías y bombillería'),
(4, 'Lubricantes y Químicos', 'Aceites 2T/4T, líquido refrigerante y desengrasantes'),
(5, 'Accesorios', 'Espejos, manillares, cortavientos y defensas');

INSERT IGNORE INTO repuestos (id, categoria_id, codigo_referencia, codigo_oem, nombre, marca_moto, precio_compra, precio_venta, stock_actual, stock_minimo, activo) VALUES
(1, 1, 'PAST-FR-FZ16', 'OEM-54B-W0045-00', 'Pastillas de Freno Delanteras Yamaha FZ16', 'Yamaha FZ16 / FZ 2.0', 18000.00, 32000.00, 12, 3, 1),
(2, 1, 'BND-TR-GN125', 'OEM-64410-05300', 'Bandas de Freno Traseras Suzuki GN125', 'Suzuki GN125', 12000.00, 22000.00, 2, 4, 1), -- En alerta de stock bajo
(3, 2, 'KIT-ARR-PULSAR200', 'OEM-36DK0012', 'Kit de Arrastre Reforzado Bajaj Pulsar 200 NS', 'Bajaj Pulsar NS200', 75000.00, 125000.00, 8, 2, 1),
(4, 3, 'BUJ-NGK-CR8E', 'NGK-1275', 'Bujía Estándar NGK CR8E', 'Universal 150cc-250cc', 9000.00, 16000.00, 25, 5, 1),
(5, 4, 'ACE-MOT-7100', 'MOT-7100-10W40', 'Aceite 100% Sintético Motul 7100 10W40 1L', 'Universal 4T', 42000.00, 62000.00, 1, 3, 1); -- En alerta de stock crítico

