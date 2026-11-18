
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

-- Catálogo de prueba: 25 productos (IDs 1-5 existentes y 6-25 nuevos)
-- Estados: 2 con stock bajo (IDs 2 y 5), 2 agotados (IDs 6 y 15) y 1 inactivo (ID 18)
INSERT IGNORE INTO repuestos (id, categoria_id, codigo_referencia, codigo_oem, nombre, marca_moto, precio_compra, precio_venta, stock_actual, stock_minimo, activo) VALUES
(1, 1, 'PAST-FR-FZ16', 'OEM-54B-W0045-00', 'Pastillas de Freno Delanteras Yamaha FZ16', 'Yamaha FZ16 / FZ 2.0', 18000.00, 32000.00, 12, 3, 1),
(2, 1, 'BND-TR-GN125', 'OEM-64410-05300', 'Bandas de Freno Traseras Suzuki GN125', 'Suzuki GN125', 12000.00, 22000.00, 2, 4, 1), -- En alerta de stock bajo
(3, 2, 'KIT-ARR-PULSAR200', 'OEM-36DK0012', 'Kit de Arrastre Reforzado Bajaj Pulsar 200 NS', 'Bajaj Pulsar NS200', 75000.00, 125000.00, 8, 2, 1),
(4, 3, 'BUJ-NGK-CR8E', 'NGK-1275', 'Bujía Estándar NGK CR8E', 'Universal 150cc-250cc', 9000.00, 16000.00, 25, 5, 1),
(5, 4, 'ACE-MOT-7100', 'MOT-7100-10W40', 'Aceite 100% Sintético Motul 7100 10W40 1L', 'Universal 4T', 42000.00, 62000.00, 1, 3, 1), -- En alerta de stock crítico
(6, 1, 'DISC-FR-PULSAR200', 'OEM-36DK0013', 'Disco de Freno Delantero Bajaj Pulsar 200 NS', 'Bajaj Pulsar NS200', 48000.00, 82000.00, 0, 2, 1), -- Agotado
(7, 2, 'CAD-520H-120', 'OEM-520H120', 'Cadena de Transmisión 520H x 120 Eslabones', 'Universal 200cc-250cc', 38000.00, 68000.00, 14, 4, 1),
(8, 3, 'BOB-CB190R', 'OEM-30510-KWPB01', 'Bobina de Encendido Honda CB 190R', 'Honda CB 190R', 28000.00, 52000.00, 11, 3, 1),
(9, 4, 'ACE-YAM-20W50', 'YAM-20W50-1L', 'Aceite Semisintético Yamalube 20W50 1L', 'Universal 4T', 24000.00, 39000.00, 20, 5, 1),
(10, 1, 'LIQ-FR-DOT4', 'DOT4-500', 'Líquido de Frenos DOT 4 500 ml', 'Universal', 14000.00, 26000.00, 18, 4, 1),
(11, 2, 'KIT-CIL-150', 'OEM-150CIL', 'Kit de Cilindro y Pistón 150cc', 'Universal 150cc', 85000.00, 145000.00, 6, 2, 1),
(12, 3, 'REG-VOL-GN125', 'OEM-32800-05300', 'Regulador de Voltaje Suzuki GN125', 'Suzuki GN125', 32000.00, 58000.00, 9, 3, 1),
(13, 4, 'LIM-INI-300', 'LIM-300', 'Limpiador de Inyectores 300 ml', 'Universal', 13000.00, 25000.00, 17, 4, 1),
(14, 5, 'ESP-IZ-FZ16', 'OEM-54B-F6280-00', 'Espejo Retrovisor Izquierdo Yamaha FZ16', 'Yamaha FZ16', 22000.00, 38000.00, 10, 3, 1),
(15, 3, 'BAT-12V-7AH', 'BAT-12V7A', 'Batería Sellada 12V 7Ah', 'Universal', 48000.00, 85000.00, 0, 2, 1), -- Agotado
(16, 5, 'MAN-DEP-22', 'MAN-22MM', 'Manillar Deportivo Universal 22 mm', 'Universal', 28000.00, 49000.00, 7, 2, 1),
(17, 5, 'DEF-MOT-PULSAR200', 'OEM-36DK0014', 'Defensa de Motor Acero Bajaj Pulsar 200 NS', 'Bajaj Pulsar NS200', 65000.00, 110000.00, 5, 2, 1),
(18, 5, 'COR-UNI-NEG', 'COR-NEG', 'Cortavientos Universal Negro', 'Universal', 30000.00, 55000.00, 6, 2, 0), -- Inactivo
(19, 1, 'PAST-FR-CB190R', 'OEM-06455-KWPB01', 'Kit de Pastillas de Freno Delanteras Honda CB 190R', 'Honda CB 190R', 22000.00, 40000.00, 13, 4, 1),
(20, 2, 'PIN-SAL-15T', 'PIN-15T', 'Piñón de Salida 15T 520', 'Universal 200cc-250cc', 18000.00, 34000.00, 16, 5, 1),
(21, 3, 'BOM-LED-H4', 'LED-H4-12V', 'Bombillo LED H4 12V', 'Universal', 15000.00, 29000.00, 22, 6, 1),
(22, 4, 'GRA-MUL-500', 'GRA-500', 'Grasa Multipropósito 500 g', 'Universal', 12000.00, 22000.00, 19, 5, 1),
(23, 5, 'SOP-CEL-MOTO', 'SOP-MOTO', 'Soporte de Celular para Moto', 'Universal', 18000.00, 35000.00, 12, 3, 1),
(24, 1, 'BOM-FR-UNI', 'BOM-FR-UNI', 'Bomba de Freno Trasera Universal', 'Universal', 35000.00, 62000.00, 8, 2, 1),
(25, 2, 'FIL-ACE-CB190R', 'OEM-15412-KWPB01', 'Filtro de Aceite Honda CB 190R', 'Honda CB 190R', 12000.00, 24000.00, 15, 4, 1);

