

| Software Architecture Document | Junio 2026 2026 |
| :---: | :---: |
| Microservicio de Incidentes – Plataforma FleetOps | FleetCorp S.A. |

| Control de Cambios |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- |
| **Creación del documento** |  |  |  |  |
| **Autor** | Equipo FleetOps | **Fecha** | Junio 2026 |  |
| **Revisado por** | **Nombre** |  | **Fecha** | Por definir |
|  | **Cargo** |  |  |  |
| **Aprobado por** | **Nombre** |  | **Fecha** | Por definir |
|  | **Cargo** |  |  |  |
| **Versión** | **Descripción** | **Autor** | **Aprobado Por** | **Fecha Aprobación** |
| 1.0 | Versión inicial del DAS | Equipo FleetOps | Por definir | Junio 2026 |

# **Introducción**

El Documento de la Arquitectura del Software (DAS) proporciona una visión general del microservicio de Incidentes de la plataforma FleetOps, desarrollado para FleetCorp S.A. Incluye el propósito, el alcance, las definiciones, las referencias y la vista global del DAS.

## **Propósito**

El presente DAS define las decisiones arquitectónicas, patrones de diseño y restricciones técnicas del microservicio de Incidentes. Está dirigido a los equipos de desarrollo, arquitectura y operaciones de FleetCorp S.A., y sirve como referencia para el diseño, implementación, revisión y evolución del servicio. El microservicio centraliza la gestión de incidentes vehiculares (accidentes, fallas, eventos de seguridad) garantizando trazabilidad, respuesta oportuna y comunicación confiable con los microservicios de Vehículos, Mantenimiento y Asignaciones.

## **Alcance**

El DAS abarca los siguientes aspectos del microservicio de Incidentes:

* Decisiones arquitecturales adoptadas y patrones de diseño seleccionados.

* Módulos y funcionalidades internas del microservicio.

* Atributos de calidad observables y no observables.

* Patrones de diseño: Arquitectura Hexagonal, Circuit Breaker, SAGA Pattern, Message Broker (RabbitMQ), BD relacional.

* Representación de la solución a través de vistas: física, funcional/lógica y de despliegue.

* Integración con los microservicios de Vehículos, Mantenimiento y Asignaciones.

## **Definiciones, siglas y abreviaturas**

* **API Gateway:** Componente que centraliza el enrutamiento, la autenticación y el control de tráfico hacia los microservicios.

* **Arquitectura Hexagonal (Ports and Adapters):** Estilo arquitectural que organiza el sistema en un núcleo de dominio aislado, rodeado de puertos (interfaces) y adaptadores (implementaciones concretas para REST, colas de mensajes y bases de datos).

* **BD:** Base de Datos relacional (PostgreSQL).

* **CI/CD:** Integración Continua / Entrega Continua (*Continuous Integration / Continuous Delivery*).

* **Circuit Breaker:** Patrón de resiliencia que detecta fallos en llamadas externas y evita cascadas de error.

* **DAS:** Documento de Arquitectura de Software.

* **Message Broker:** Intermediario de mensajería (ej. RabbitMQ) utilizado para la comunicación asíncrona entre microservicios.

* **REST:** *Representational State Transfer* (Transferencia de Estado Representacional). Estilo arquitectural para APIs web.

* **SAGA Pattern:** Patrón de coordinación de transacciones distribuidas mediante pasos compensatorios.

## **Referencias**

| Documento | Versión | Fecha de la versión |
| :---- | :---- | :---- |
| Product Backlog – Plataforma FleetOps | 1.0 | Junio 2026 |
| Requerimientos Microservicio Incidentes | 1.0 | Junio 2026 |

## **Vista Global**

El documento se organiza en las siguientes secciones:

* Sección 1 – Introducción: propósito, alcance, definiciones y referencias.

* Sección 2 – Macro Arquitectura: descripción de capas, metas y restricciones arquitectónicas con tablas de atributos de calidad observables y no observables.

* Sección 3 – Vista Física: infraestructura de contenedores, base de datos y bus de mensajería.

* Sección 4 – Vista Funcional o Lógica: componentes internos, casos de uso, integraciones y patrones aplicados.

* Sección 5 – Vista de Despliegue: nodos, CI/CD y stack tecnológico.

El microservicio adopta una arquitectura hexagonal (Ports and Adapters), organizada en tres zonas:

* **Núcleo de dominio:** contiene la lógica de negocio pura (gestión de incidentes, reglas de gravedad, coordinación de flujos). No depende de ninguna tecnología externa.

* **Puertos de entrada (Driving Adapters):** adaptador REST API que recibe solicitudes de usuarios (conductores, coordinadores, administradores) a través del API Gateway.

* **Puertos de salida (Driven Adapters):** adaptador de BD (ORM Django → PostgreSQL) y adaptador de mensajería (productor/consumidor RabbitMQ → microservicios externos).

# **Macro Arquitectura**

El microservicio de Incidentes adopta una arquitectura hexagonal (Ports and Adapters) dentro del ecosistema de microservicios de FleetOps. Esta arquitectura aísla el núcleo de dominio de las tecnologías externas, conectándose al mundo exterior mediante dos tipos de adaptadores:

* **REST API:** canal exclusivo de interacción con usuarios (conductores, coordinadores, administradores) a través del API Gateway.

* **Message Broker (RabbitMQ):** canal exclusivo de comunicación asíncrona con los microservicios de Vehículos, Mantenimiento y Asignaciones. Toda coordinación entre servicios ocurre por esta vía.

Los patrones arquitectónicos complementarios son: Circuit Breaker (resiliencia en el adaptador REST de entrada), SAGA Pattern (coordinación de transacciones distribuidas a través del adaptador de mensajería) y BD relacional PostgreSQL (persistencia en el adaptador de salida). Los registros de incidentes son inmutables una vez creados; no se actualiza su estado.

Flujo de dependencias en la arquitectura hexagonal:

* Adaptador REST (entrada) → Núcleo de dominio: el adaptador REST transforma la solicitud HTTP y llama al caso de uso correspondiente en el dominio.

* Núcleo de dominio → Adaptador BD (salida): el dominio persiste el incidente en PostgreSQL a través del puerto de repositorio, implementado con el ORM de Django.

* Núcleo de dominio → Adaptador de mensajería (salida): el dominio pública el evento al puerto de mensajería, implementado con RabbitMQ, al completar el registro del incidente.

* Adaptador de mensajería (entrada) → Núcleo de dominio: el adaptador de consumo de colas recibe confirmaciones de otros microservicios e invoca los casos de uso correspondientes.

## **Metas y Restricciones Arquitectónicas**

| Atributos de Calidad "Observables" |  |  |  |
| ----- | :---- | :---- | :---- |
| **Atributo de Calidad** | **Descripción** | **Tácticas / Patrón de Diseño** | **Donde se aplica** |
| **Disponibilidad** | Capacidad del sistema de estar operativo al ser requerido, manejando eficazmente las fallas que puedan afectar su funcionamiento. | Patrón: Circuit Breaker. Detecta fallos en las llamadas REST y evita cascadas de error. Patrón: Sincronización de estado para verificar disponibilidad de dependencias. | Endpoints REST expuestos a usuarios. Llamadas hacia microservicios de Vehículos, Mantenimiento y Asignaciones vía Message Broker. |
| **Trazabilidad** | Todo incidente queda registrado con su historial completo de cambios de estado, auditable en cualquier momento. | BD relacional exclusiva con registros de incidentes inmutables. La trazabilidad se obtiene consultando el historial de registros por conductor, vehículo o fecha. | Módulo de gestión del estado. Tablas de historial en PostgreSQL. |
| **Resiliencia** | Tolerancia a fallos en la comunicación con otros microservicios, sin afectar la operación principal del servicio de incidentes. | Circuit Breaker: aísla fallos en llamadas REST. Message Broker (RabbitMQ) con reintentos y dead-letter queues para mensajes fallidos. SAGA Pattern para coordinar transacciones distribuidas con pasos compensatorios. | Comunicación asíncrona con Vehículos, Mantenimiento y Asignaciones. Endpoints REST de usuarios. |
| **Seguridad** | Acceso controlado a los endpoints; datos de entrada validados en cada operación. | API Gateway como proxy centralizado: autenticación, autorización y control de tráfico. Validación de datos en la capa de API REST. | Todos los endpoints del microservicio expuestos vía API Gateway. |
| **Integridad de Datos** | Los datos de incidentes son consistentes y válidos en todo momento, incluso ante fallos parciales. | SAGA Pattern: coordina transacciones distribuidas con compensaciones. Validaciones en endpoints REST. Pruebas unitarias obligatorias con cobertura mínima definida. | Endpoints de registro y actualización de incidentes. Flujos distribuidos con Vehículos, Mantenimiento y Asignaciones. |
| **Despliegue Automatizado** | Cada cambio validado se despliega de forma automática y reproducible. | Pipeline CI/CD con GitHub Actions: build, pruebas unitarias, análisis estático (Sonar Cloud) y despliegue en contenedor Docker. | Repositorio GitHub del microservicio. Ambiente de integración continua. |

| Atributos de Calidad "No Observables" |  |  |  |
| ----- | :---- | :---- | :---- |
| **Atributo** | **Descripción** | **Tácticas / Patrón de Arquitectura** | **Donde se aplica** |
| **Modificabilidad** | Habilidad de realizar cambios futuros al sistema con bajo impacto en otros módulos (Bosch et al., 1999). | Arquitectura Hexagonal (Ports and Adapters): el núcleo de dominio es independiente de los adaptadores. Reemplazar REST por otro protocolo o cambiar de BD requiere solo cambiar el adaptador, sin tocar el dominio. Comunicación asíncrona vía Message Broker para desacoplar servicios. | Toda la estructura del microservicio de incidentes. Interfaces de comunicación con otros microservicios. |
| **Mantenibilidad** | Capacidad de modificar el sistema de manera rápida y a bajo costo (Barbacci et al., 1995). | Código versionado en GitHub con ramas y Pull Requests. Análisis estático con SonarCloud. Pipeline CI/CD automatizado. Estandarización de nombres y estructura de código. | Repositorio GitHub. Pipeline de CI/CD con GitHub Actions. |
| **Escalabilidad** | Capacidad de ampliar el servicio para soportar el crecimiento de la flota sin degradación del rendimiento (Pressman, 2002). | Contenedores Docker: cada instancia es replicable horizontalmente. BD PostgreSQL independiente. API sin estado en la capa REST. | Contenedores Docker del microservicio. Base de datos PostgreSQL. |
| **Facilidad de Integración** | Capacidad de comunicarse con los microservicios de Vehículos, Mantenimiento y Asignaciones de forma desacoplada. | REST API estandarizada para usuarios. Message Broker (RabbitMQ) para comunicación asíncrona con otros microservicios. API Gateway como punto único de entrada. | Canal REST con usuarios (conductores, coordinadores, administradores). Canal de mensajería con microservicios internos. |

### 

### **Restricciones Técnicas**

* Arquitectura exclusivamente backend, sin capa de presentación propia.

* Arquitectura basada en microservicios con comunicación REST hacia usuarios y mensajería asíncrona (RabbitMQ) hacia otros microservicios.

* Base de datos relacional propia por microservicio (PostgreSQL). Los registros de incidentes son inmutables; no se actualiza su estado.

* Patrones obligatorios: Circuit Breaker, SAGA Pattern, Message Broker.

* Gestión de versiones y CI/CD mediante GitHub y GitHub Actions.

* Despliegue en contenedores Docker.

* Framework Django REST Framework.

# **Vista Física**

La vista física describe la distribución y despliegue del microservicio de Incidentes en infraestructura de contenedores. Cada componente se despliega de forma independiente para garantizar aislamiento, escalabilidad y tolerancia a fallos.

**Nodos físicos:**

* Contenedor Docker – Microservicio de Incidentes: ejecuta la aplicación Django REST Framework con la lógica de negocio y la API REST. Expuesto únicamente a través de la API Gateway.

* Contenedor Docker – PostgreSQL: base de datos relacional exclusiva del microservicio. Almacena los registros de incidentes (inmutables). Sin acceso externo directo.

* API Gateway: punto de entrada unificado que recibe las solicitudes REST de usuarios y las redirige al microservicio. Centraliza autenticación, autorización y control de tráfico.

* RabbitMQ (Message Broker): nodo de mensajería para la comunicación asíncrona. Recibe eventos publicados por el microservicio de Incidentes y los distribuye a Vehículos, Mantenimiento y Asignaciones.

Flujo de interacciones físicas:

1. El usuario (conductor/coordinador/administrador) envía una solicitud REST al API Gateway.

2. El API Gateway auténtica/autoriza y redirige al contenedor del microservicio de Incidentes.

3. El microservicio procesa la solicitud, aplica la lógica de negocio y escribe el resultado en PostgreSQL.

4. Si el incidente amerita notificar a otros servicios, el microservicio publica un evento a RabbitMQ.

5. Los microservicios de Vehículos, Mantenimiento y Asignaciones consumen el evento de forma autónoma y reaccionan según sus propias reglas.

Todos los contenedores se gestionan mediante Docker Compose o un orquestador compatible, garantizando portabilidad y reproducibilidad del entorno.

# **Vista Funcional o Lógica**

La Vista Funcional describe los componentes internos del microservicio de Incidentes, sus responsabilidades y las interacciones entre ellos y con los microservicios externos de la plataforma FleetOps.

## **Componentes Internos**

El microservicio se organiza en tres zonas de la arquitectura hexagonal:

**Núcleo de dominio (lógica de negocio pura):**

* Caso de uso – Registrar Incidente: orquesta la validación de placa, la persistencia del registro y la publicación del evento.

* Caso de uso – Consultar Incidentes: ejecuta las consultas filtradas por tipo, gravedad, conductor, placa o fecha.

* Reglas de negocio: determina qué tipo de evento publicar según el tipo (HUMANO / MECANICO) y gravedad (LEVE / GRAVE) del incidente.

**Adaptadores de entrada (Driving Adapters):**

* Adaptador REST API (Django REST Framework): recibe las solicitudes HTTP de usuarios (conductores, coordinadores, administradores) a través del API Gateway y las traduce en llamadas a los casos de uso del dominio.

* Adaptador de Cola de Entrada (RabbitMQ Consumer): recibe mensajes de otros microservicios (ej. confirmaciones) y los traduce en llamadas al dominio.

**Adaptadores de salida (Driven Adapters):**

* Adaptador de Repositorio (ORM Django → PostgreSQL): implementa el puerto de persistencia del dominio. Escribe los registros de incidentes en la BD. Los registros son inmutables una vez creados.

* Adaptador de Cola de Salida (RabbitMQ Producer): implementa el puerto de mensajería del dominio. Publica los eventos al broker para que los microservicios de Vehículos, Mantenimiento y Asignaciones los consuman.

## **Casos de Uso / Historias de Usuario**

1. Como conductor, deseo registrar un incidente asociado a un vehículo y/o conductor, especificando la gravedad y detalles del evento.  
2. Como administrador o coordinador, deseo acceder al registro histórico de incidentes, filtrables por vehículo, conductor, rango de fechas y gravedad.  
3. Como sistema, deseo que, al registrar un incidente, el vehículo sea marcado como no disponible en la BD hasta la revisión por mantenimiento (excepto si la gravedad es leve).  
4. Como coordinador, deseo que el registro de un incidente no leve publique automáticamente un evento al broker para que Mantenimiento inicie el flujo de revisión.  
5. Como conductor o coordinador, deseo que, si la gravedad del incidente es leve, el evento notifique la demora estimada a Asignaciones, evitando bloqueos o reasignaciones innecesarias.

## **Integración con Otros Microservicios**

El microservicio de Incidentes se comunica con usuarios vía REST API y con otros microservicios exclusivamente mediante eventos publicados al Message Broker (RabbitMQ):

* Microservicio de Vehículos: consume el evento de incidente registrado y actualiza la disponibilidad del vehículo afectado en su propia BD. El microservicio de Incidentes no llama directamente a Vehículos.

* Microservicio de Mantenimiento: consume el evento de incidente no leve para iniciar automáticamente el flujo de revisión y reparación. El patrón SAGA coordina esta transacción distribuida con pasos compensatorios en caso de fallo.

* Microservicio de Asignaciones: consume el evento de incidente para evaluar la reasignación del vehículo o conductor afectado. En incidentes leves, recibe la demora estimada sin forzar una reasignación.

## **Patrones de Diseño Aplicados**

* API Gateway: centraliza seguridad, autenticación y enrutamiento del tráfico REST de usuarios.

* Circuit Breaker: protege la capa REST ante fallos o latencias excesivas, evitando que un fallo puntual degrade todo el servicio.

* Message Broker (RabbitMQ): desacopla completamente el microservicio de Incidentes de los microservicios de Vehículos, Mantenimiento y Asignaciones. Incluye reintentos y dead-letter queues para mensajes fallidos.

* SAGA Pattern: coordina el flujo distribuido (registrar incidente → notificar a Vehículos \+ Mantenimiento \+ Asignaciones) como una cadena de pasos con compensaciones en caso de fallo parcial.

* BD Relacional \+ Tablas de Auditoría: el estado de cada incidente y sus transiciones se persisten directamente en PostgreSQL con registros de auditoría para trazabilidad completa.

* Log Aggregation: centralización de logs del microservicio para auditoría, monitoreo operacional e investigación de incidentes.

# **Vista de Despliegue**

La Vista de Despliegue describe cómo el microservicio de Incidentes se ejecuta y distribuye en nodos físicos o virtuales, y cómo se interconectan en el entorno de producción.

## **Nodos y Configuración**

* Nodo 1 – Microservicio de Incidentes: contenedor Docker ejecutando Django REST Framework. Se conecta al nodo de PostgreSQL para persistencia y al nodo de RabbitMQ para publicación/consumo de eventos.

* Nodo 2 – PostgreSQL: contenedor Docker dedicado exclusivamente a la persistencia de registros de incidentes del microservicio. Sin acceso externo directo. Los registros son inmutables.

* Nodo 3 – API Gateway: recibe todo el tráfico REST de usuarios y lo enruta al microservicio. Gestiona autenticación, autorización y control de tráfico.

* Nodo 4 – RabbitMQ: broker de mensajería para la comunicación asíncrona entre microservicios. Configurado con dead-letter queues y políticas de reintento.

## **Desarrollo y CI/CD**

* Código versionado en GitHub con estrategia de ramas (main, develop, feature/\*, hotfix/\*).

* Pull Requests obligatorios con revisión de código antes de merge a ramas principales.

* Pipeline CI/CD con GitHub Actions: build, ejecución de pruebas unitarias, análisis estático con SonarCloud y despliegue automático en ambiente de integración.

* Cobertura de pruebas unitarias obligatoria con umbral mínimo definido en el pipeline.

## **Riesgos y Deuda Técnica**

* Riesgo de inconsistencia eventual entre microservicios si el broker falla; mitigado con dead-letter queues, políticas de reintento y el patrón SAGA con compensaciones.

* Complejidad en la gestión de transacciones distribuidas; mitigado con implementación explícita de SAGA y logs centralizados.

* Dependencia del correcto levantamiento y rendimiento de RabbitMQ; requiere monitoreo activo y alta disponibilidad del broker.

* La integración rápida puede descuidar cobertura de pruebas; mitigado con umbrales de cobertura obligatorios en el pipeline CI/CD.

## **Stack Tecnológico**

| Componente | Tecnología |
| :---- | :---- |
| **Framework** | Django REST Framework |
| **Base de Datos** | PostgreSQL (BD relacional por microservicio) |
| **Arquitectura** | Microservicios |
| **Control de Versiones** | GitHub |
| **CI/CD** | GitHub Actions |
| **Contenedorización** | Docker |
| **Message Broker** | RabbitMQ |
| **Análisis de Código** | SonarCloud |

# **Modelo de Datos y Flujos de Trabajo**

Esta sección describe el modelo de base de datos del microservicio de Incidentes y los flujos de trabajo que se ejecutan ante cada tipo de evento.

## **Modelo de Base de Datos**

El microservicio de Incidentes posee su propia base de datos PostgreSQL exclusiva. La entidad principal es la tabla Incidentes, definida a continuación:

| Modelo de Base de Datos – Tabla: incidentes |  |  |  |
| ----- | :---- | :---- | :---- |
| **Campo** | **Tipo de Dato** | **Restricción** | **Descripción** |
| **id\_incidente** | UUID / SERIAL | PK, NOT NULL | Identificador único del incidente. Generado automáticamente. |
| **fecha\_hora** | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha y hora exacta en que ocurrió el incidente. |
| **id\_conductor** | VARCHAR / UUID | NOT NULL, FK | Identificador del conductor que reporta el incidente. Referencia al microservicio de conductores. |
| **tipo\_incidente** | ENUM | NOT NULL | Categoría del incidente. Valores permitidos: HUMANO | MECÁNICO. |
| **gravedad** | ENUM | NOT NULL | Nivel de gravedad del incidente. Valores permitidos: LEVE | GRAVE. |
| **descripcion** | TEXT | NULLABLE | Descripción detallada del incidente reportada por el conductor. |
| **placa\_vehiculo** | VARCHAR(20) | NOT NULL | Placa del vehículo involucrado. Validada contra el microservicio de Vehículos antes del registro. |

Nota: los registros de incidentes son inmutables una vez creados; no se actualizan ni tienen campo de estado. Los campos id\_conductor y placa\_vehiculo no son claves foráneas directas a otras BDs (cada microservicio gestiona su propia BD). La validación de la placa se realiza en tiempo de solicitud consultando al microservicio de Vehículos antes de persistir el registro.

## **Flujos de Trabajo**

### **Flujo 1 – Validación de placa y registro del incidente**

Cuando un cliente (conductor, coordinador) envía una solicitud POST al REST API del microservicio de Incidentes, se ejecuta el siguiente flujo de validación previo al registro:

| Paso | Actor / Componente | Acción |
| :---: | :---- | :---- |
| 1 | API Gateway | Recibe la solicitud REST, autentica y autoriza al usuario. Redirige al microservicio de Incidentes. |
| 2 | Microservicio Incidentes | Recibe los datos del incidente (placa, id\_conductor, tipo, gravedad, descripción, fecha\_hora). |
| 3 | Microservicio Incidentes → Microservicio Vehículos | Consulta REST (síncrona) al microservicio de Vehículos para verificar que la placa esté registrada en el sistema. Esta es la única llamada REST directa entre microservicios; está protegida con Circuit Breaker. |
| 4a | Microservicio Incidentes | Si la placa NO está registrada: retorna error HTTP 422 al cliente con mensaje 'Placa no registrada en el sistema'. No se persiste ningún dato. |
| 4b | Microservicio Incidentes | Si la placa SÍ está registrada: persiste el incidente (registro inmutable) en la BD PostgreSQL y continúa al Flujo 2\. |

### **Flujo 2 – Activación del flujo de trabajo según tipo y gravedad**

Una vez validada la placa y persistido el incidente, el microservicio publica un evento al Message Broker (RabbitMQ). El tipo y gravedad del incidente determinan qué microservicios reaccionan y cómo:

**Caso A – Incidente Mecánico Grave:**

| Paso | Actor / Componente | Acción |
| :---: | :---- | :---- |
| 1 | Microservicio Incidentes | Pública evento incidente\_mecanico\_grave al broker con los datos del incidente. |
| 2 | Microservicio Vehículos | Consume el evento y marca el vehículo como NO DISPONIBLE en su BD. Publica confirmación vehiculo\_bloqueado. |
| 3 | Microservicio Asignaciones | Consume el evento y asigna un vehículo de reemplazo al conductor afectado. Publica confirmación vehiculo\_reasignado. |
| 4 | Microservicio Mantenimiento | Consume el evento y agenda una orden de mantenimiento para el vehículo afectado. Publica confirmación mantenimiento\_agendado. |
| 5 | Microservicio Incidentes | Espera confirmación de los tres servicios (vehiculo\_bloqueado \+ vehiculo\_reasignado \+ mantenimiento\_agendado). El patrón SAGA coordina estos pasos; si alguno falla, se ejecutan acciones compensatorias. Al recibir todas las confirmaciones, actualiza el estado del incidente a EN\_GESTION. |

**Caso B – Incidente Mecánico Leve:**

| Paso | Actor / Componente | Acción |
| :---: | :---- | :---- |
| 1 | Microservicio Incidentes | Pública evento incidente\_mecanico\_leve al broker con la demora estimada del servicio. |
| 2 | Microservicio Asignaciones | Consume el evento y notifica al servicio afectado sobre el retraso estimado. No reasigna vehículo ni conductor. |
| 3 | Microservicio Incidentes | Al recibir la confirmación de Asignaciones, actualiza el estado del incidente a EN\_GESTION. El vehículo no está bloqueado; no se agenda mantenimiento. |

**Caso C – Incidente Humano (leve o grave):**

| Paso | Actor / Componente | Acción |
| :---: | :---- | :---- |
| 1 | Microservicio Incidentes | Pública evento incidente\_humano al broker con los datos del vehículo y servicio afectado. |
| 2 | Microservicio Asignaciones | Consume el evento y asigna un nuevo conductor al vehículo asociado al servicio. Publica confirmación conductor\_reasignado. |
| 3 | Microservicio Incidentes | Al recibir la confirmación conductor\_reasignado, actualiza el estado del incidente a EN\_GESTION. |

### **Flujo 3 – Consulta de incidentes por el Servicio de Reportes**

El Servicio de Reportes puede consultar la información de la BD de incidentes directamente a través de los endpoints REST del microservicio. Las consultas están protegidas por el API Gateway (autenticación y autorización de solo lectura para el rol de Reportes).

| Filtro de Consulta | Parámetro | Descripción |
| :---- | :---- | :---- |
| **Por tipo de incidente** | tipo\_incidente | Retorna todos los incidentes de tipo HUMANO o MECÁNICO. |
| **Por gravedad** | gravedad | Retorna todos los incidentes de gravedad LEVE o GRAVE. |
| **Por conductor** | id\_conductor | Retorna todos los incidentes reportados por un conductor específico. |
| **Por placa de vehículo** | placa\_vehiculo | Retorna todos los incidentes asociados a una placa de vehículo específica. |
| **Por rango de fechas** | fecha\_desde / fecha\_hasta | Retorna incidentes ocurridos dentro de un rango de fechas determinado. |
| **Combinación de filtros** | Múltiples parámetros | Los filtros anteriores pueden combinarse en una misma consulta para obtener resultados más específicos. |

El Servicio de Reportes accede a los datos directamente vía REST GET al microservicio de Incidentes; no tiene acceso directo a la BD PostgreSQL. Esto garantiza que toda consulta pase por la capa de seguridad del API Gateway y la lógica de autorización del microservicio.

