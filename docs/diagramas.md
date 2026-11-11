# Diagramas del Sistema «AllQuality»

**Proyecto:** Sistema de Gestión Comercial de Repuestos para Motocicletas  
**Asignatura:** Ingeniería de Software II — COTECNOVA 2026-2  
**Responsable de documentación:** Santiago Calvo

> Las versiones principales están en **imágenes PNG** dentro de [`docs/diagramas/`](diagramas/). Cada sección conserva el código Mermaid en un bloque desplegable para que el diagrama pueda editarse y regenerarse. Las imágenes usan un tema neutro en blanco, negro y grises para mantener la misma línea visual del frontend.

## Índice

1. [Base de datos](#base-datos)
2. [Arquitectura general](#arquitectura)
3. [Navegación del frontend](#navegacion)
4. [Casos de uso por rol](#casos-uso)
5. [Registro de una venta](#venta)
6. [Ajuste de inventario](#inventario)
7. [Despliegue local](#despliegue)

---

<a id="base-datos"></a>
## 1. Base de datos

Vista simplificada del modelo entidad-relación. Las cajas representan tablas, `PK` identifica la clave primaria y `FK` las llaves foráneas. El diccionario completo de campos está en [`modelo-datos.md`](modelo-datos.md).

![Modelo entidad-relación de AllQuality](diagramas/01-base-datos.png)

### Cómo leerlo

- Un **rol** puede tener muchos **usuarios**.
- Una **categoría** agrupa muchos **repuestos**.
- Un **usuario** registra muchas **ventas**.
- Una **venta** contiene varias líneas en **detalle_ventas**.
- Un **repuesto** puede aparecer en muchas ventas y en muchos movimientos de auditoría.
- `detalle_ventas` une ventas y repuestos; conserva la cantidad y el precio del momento de la venta.

### Relaciones principales

| Relación | Cardinalidad | Para qué sirve |
| :--- | :---: | :--- |
| `roles` → `usuarios` | 1:N | Define los permisos del usuario. |
| `categorias` → `repuestos` | 1:N | Organiza el catálogo. |
| `usuarios` → `ventas` | 1:N | Identifica quién vendió. |
| `ventas` → `detalle_ventas` | 1:N | Guarda los productos de la factura. |
| `repuestos` → `detalle_ventas` | 1:N | Relaciona cada línea con su producto. |
| `repuestos` → `auditoria_movimientos` | 1:N | Historial de entradas y salidas. |
| `usuarios` → `auditoria_movimientos` | 1:N | Identifica quién hizo el movimiento. |

<details>
<summary>Ver código Mermaid del diagrama</summary>

```mermaid
%%{init: {'theme': 'neutral'}}%%
erDiagram
    ROLES ||--o{ USUARIOS : asigna
    CATEGORIAS ||--o{ REPUESTOS : clasifica
    USUARIOS ||--o{ VENTAS : registra
    VENTAS ||--|{ DETALLE_VENTAS : contiene
    REPUESTOS ||--o{ DETALLE_VENTAS : se_vende_en
    REPUESTOS ||--o{ AUDITORIA_MOVIMIENTOS : genera
    USUARIOS ||--o{ AUDITORIA_MOVIMIENTOS : realiza

    ROLES {
        int id PK
        string nombre
    }

    USUARIOS {
        int id PK
        int rol_id FK
        string nombre
        string email
        boolean activo
    }

    CATEGORIAS {
        int id PK
        string nombre
    }

    REPUESTOS {
        int id PK
        int categoria_id FK
        string codigo_referencia
        string nombre
        decimal precio_venta
        int stock_actual
        int stock_minimo
    }

    VENTAS {
        int id PK
        int usuario_id FK
        string numero_factura
        decimal total
        string estado
    }

    DETALLE_VENTAS {
        int id PK
        int venta_id FK
        int repuesto_id FK
        int cantidad
        decimal subtotal
    }

    AUDITORIA_MOVIMIENTOS {
        int id PK
        int repuesto_id FK
        int usuario_id FK
        string tipo_movimiento
        int cantidad
    }
```
</details>

---

<a id="arquitectura"></a>
## 2. Arquitectura general

El frontend y el backend son dos aplicaciones separadas que se comunican por HTTP/JSON. La base de datos solo es accesible desde el backend.

![Arquitectura general de AllQuality](diagramas/02-arquitectura.png)

### Capas

| Capa | Tecnología | Responsabilidad |
| :--- | :--- | :--- |
| Interfaz | React + Vite | Login, catálogo, inventario y ventas. |
| API | Flask | Recibe peticiones, valida la sesión y devuelve JSON. |
| Negocio | Servicios Python | Valida precios, stock, ventas y auditoría. |
| Datos | MySQL / MariaDB InnoDB | Guarda usuarios, productos, ventas y movimientos. |

<details>
<summary>Ver código Mermaid del diagrama</summary>

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    subgraph FRONTEND["FRONTEND · React"]
        UI["Interfaz web<br/>blanco y negro"]
    end

    subgraph BACKEND["BACKEND · Flask"]
        API["Rutas / API REST"]
        SERV["Servicios de negocio"]
    end

    DB[("MySQL / MariaDB<br/>allquality_db")]

    UI -->|"HTTP / JSON"| API
    API --> SERV
    SERV -->|"SQL"| DB

    classDef black fill:#111111,stroke:#111111,color:#ffffff;
    classDef white fill:#ffffff,stroke:#111111,color:#111111;
    class UI,API black
    class SERV white
```
</details>

---

<a id="navegacion"></a>
## 3. Navegación del frontend

Mapa de pantallas de la aplicación web.

![Navegación del frontend](diagramas/03-navegacion.png)

- **Panel principal:** resume productos, alertas y ventas recientes.
- **Productos:** buscar, crear, editar y desactivar repuestos.
- **Inventario:** consultar alertas y ajustar existencias.
- **Ventas:** registrar una venta o consultar el historial.

<details>
<summary>Ver código Mermaid del diagrama</summary>

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    LOGIN["Iniciar sesión"] --> DASH["Panel principal"]
    DASH --> PROD["Productos"]
    DASH --> INV["Inventario"]
    DASH --> SALES["Ventas"]

    PROD --> PROD_NEW["Nuevo producto"]
    PROD --> PROD_EDIT["Editar producto"]

    INV --> ALERT["Ver alertas"]
    INV --> ADJ["Ajustar existencias"]

    SALES --> SALE_NEW["Nueva venta"]
    SALES --> SALE_HIST["Historial de ventas"]
    SALE_HIST --> SALE_DETAIL["Detalle de factura"]

    classDef page fill:#ffffff,stroke:#111111,stroke-width:1.5px,color:#111111;
    classDef action fill:#f5f5f5,stroke:#999999,color:#111111;
    class LOGIN,DASH,PROD,INV,SALES page;
    class PROD_NEW,PROD_EDIT,ALERT,ADJ,SALE_NEW,SALE_HIST,SALE_DETAIL action;
```
</details>

---

<a id="casos-uso"></a>
## 4. Casos de uso por rol

Vista rápida de qué puede hacer cada tipo de usuario.

![Casos de uso por rol](diagramas/04-casos-uso.png)

| Rol | Puede hacer |
| :--- | :--- |
| **ADMIN** | Todo: productos, inventario, ventas y consultas. |
| **VENDEDOR** | Consultar productos, registrar ventas y ver el historial. |
| **INVENTARIO** | Consultar productos, crear/editar repuestos, ver alertas, ajustar stock y registrar ventas. |

<details>
<summary>Ver código Mermaid del diagrama</summary>

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TB
    subgraph ADMIN["ADMIN"]
        direction LR
        A(["ADMIN"]) --> A1["Iniciar sesión"]
        A --> A2["Catálogo: consultar, crear, editar y desactivar"]
        A --> A3["Inventario: alertas y ajustar stock"]
        A --> A4["Ventas: registrar e historial"]
    end

    subgraph VEND["VENDEDOR"]
        direction LR
        V(["VENDEDOR"]) --> V1["Iniciar sesión"]
        V --> V2["Catálogo: consultar"]
        V --> V3["Ventas: registrar e historial"]
    end

    subgraph INV["INVENTARIO"]
        direction LR
        I(["INVENTARIO"]) --> I1["Iniciar sesión"]
        I --> I2["Catálogo: consultar, crear y editar"]
        I --> I3["Inventario: alertas y ajustar stock"]
        I --> I4["Ventas: registrar e historial"]
    end
```
</details>

---

<a id="venta"></a>
## 5. Registro de una venta

Flujo principal del sistema. Si un producto no tiene stock, la venta completa se cancela.

![Secuencia de registro de una venta](diagramas/05-venta.png)

### Reglas importantes

- El stock se bloquea con `FOR UPDATE` mientras dura la venta.
- Si un solo producto falla, se revierte toda la operación.
- Cada producto vendido genera un movimiento de auditoría.
- El precio se guarda en la línea de la factura para conservar el historial.

<details>
<summary>Ver código Mermaid del diagrama</summary>

```mermaid
%%{init: {'theme': 'neutral'}}%%
sequenceDiagram
    autonumber
    actor V as Vendedor
    participant F as Frontend
    participant A as API Flask
    participant S as VentaService
    participant DB as MySQL / MariaDB

    V->>F: Selecciona productos y confirma
    F->>A: POST /api/v1/ventas
    A->>S: registrar_venta(usuario_id, items)
    S->>DB: Consulta stock con FOR UPDATE
    DB-->>S: Stock y precio actual

    alt Hay stock suficiente
        S->>DB: Inserta venta y detalle
        S->>DB: Descuenta stock y registra auditoría
        S->>DB: COMMIT
        S-->>A: Venta creada
        A-->>F: 201 Created
        F-->>V: Muestra la factura
    else Falta stock
        S->>DB: ROLLBACK
        S-->>A: Error de stock
        A-->>F: 400 Bad Request
        F-->>V: Muestra el mensaje de error
    end
```
</details>

---

<a id="inventario"></a>
## 6. Ajuste de inventario

Flujo para sumar o restar existencias manualmente.

![Flujo de ajuste de inventario](diagramas/06-inventario.png)

- La cantidad puede ser positiva (entrada) o negativa (salida).
- El sistema nunca permite dejar el stock en negativo.
- Todo ajuste queda registrado con usuario, fecha y justificación.

<details>
<summary>Ver código Mermaid del diagrama</summary>

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    START["Seleccionar producto y cantidad"] --> VAL{"¿Datos completos?"}
    VAL -- No --> ERR1["Mostrar error"]
    VAL -- Sí --> LOAD["Consultar stock actual"]
    LOAD --> EXISTS{"¿Producto activo?"}
    EXISTS -- No --> ERR2["Mostrar error"]
    EXISTS -- Sí --> CALC["Calcular nuevo stock"]
    CALC --> NEG{"¿Nuevo stock menor que cero?"}
    NEG -- Sí --> ERR3["Rechazar ajuste"]
    NEG -- No --> SAVE["Guardar nuevo stock"]
    SAVE --> AUDIT["Registrar movimiento de auditoría"]
    AUDIT --> OK["Mostrar resultado"]

    classDef step fill:#ffffff,stroke:#111111,color:#111111;
    classDef danger fill:#ffffff,stroke:#b00020,color:#b00020;
    class START,LOAD,CALC,SAVE,AUDIT,OK step;
    class ERR1,ERR2,ERR3 danger;
```
</details>

---

<a id="despliegue"></a>
## 7. Despliegue local

La aplicación se ejecuta en el equipo del estudiante o evaluador, sin Docker.

![Despliegue local de AllQuality](diagramas/07-despliegue.png)

| Componente | Puerto | Comando |
| :--- | :---: | :--- |
| Frontend | `5173` | `cd src/frontend && npm run dev` |
| Backend | `5000` | `cd src/backend && python app.py` |
| MySQL / MariaDB | `3306` | Iniciar MySQL desde XAMPP o Laragon. |

<details>
<summary>Ver código Mermaid del diagrama</summary>

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    subgraph PC["Equipo local"]
        BROWSER["Navegador<br/>localhost:5173"]
        FRONT["Frontend React<br/>Vite :5173"]
        BACK["Backend Flask<br/>:5000"]
        DB[("MySQL / MariaDB<br/>:3306")]
    end

    BROWSER --> FRONT
    FRONT -->|"API REST"| BACK
    BACK -->|"SQL"| DB

    classDef app fill:#111111,stroke:#111111,color:#ffffff;
    classDef data fill:#ffffff,stroke:#111111,color:#111111;
    class FRONT,BACK app;
    class BROWSER,DB data;
```
</details>

---

**AllQuality — Ingeniería de Software II — COTECNOVA 2026-2**
