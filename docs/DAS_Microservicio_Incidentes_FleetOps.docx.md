| Software Architecture Document | Julio 2026 |
| :---: | :---: |
| Microservicio de Incidentes – Plataforma FleetOps | FleetCorp S.A. |

| Control de Cambios |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- |
| **Creación del documento** |  |  |  |  |
| **Autor** | Equipo de Incidentes | **Fecha** | Julio 2026 |  |
| **Revisado por** | **Nombre** |  | **Fecha** | Por definir |
|  | **Cargo** |  |  |  |
| **Aprobado por** | **Nombre** |  | **Fecha** | Por definir |
|  | **Cargo** |  |  |  |
| **Versión** | **Descripción** | **Autor** | **Aprobado Por** | **Fecha Aprobación** |
| 2.0 | Versión beta del DAS | Equipo de Incidentes | Por definir | N/A |

# **Introducción**

El Documento de la Arquitectura del Software (DAS) proporciona una visión general del microservicio de Incidentes de la plataforma FleetOps, desarrollado para FleetCorp S.A. Este documento resume el propósito, el alcance, las definiciones, las referencias y la vista global del sistema según la implementación actual del código.

## **Propósito**

El presente DAS define las decisiones arquitectónicas y patrones de diseño del microservicio de Incidentes. Está dirigido a los equipos de desarrollo, arquitectura y operaciones de FleetCorp S.A., y sirve como referencia para el diseño, implementación, revisión y evolución del servicio. El microservicio centraliza el registro y consulta de incidentes vehiculares, valida placas contra el microservicio de Vehículos y publica eventos de dominio para el resto del ecosistema FleetOps.

## **Alcance**

El DAS abarca los siguientes aspectos del microservicio de Incidentes:

* Decisiones arquitecturales adoptadas y patrones de diseño seleccionados.
* Módulos y funcionalidades internas del microservicio.
* Atributos de calidad observables y no observables.
* Patrones de diseño: Arquitectura Hexagonal, Circuit Breaker, Message Broker (SNS con fan-out hacia colas SQS), BD relacional.
* Integración con el microservicio de Vehículos y publicación asíncrona de eventos hacia el ecosistema.

## **Definiciones, siglas y abreviaturas**

* **API Gateway:** Componente que centraliza el enrutamiento, la autenticación y el control de tráfico hacia los microservicios.
* **Arquitectura Hexagonal (Ports and Adapters):** Estilo arquitectural que organiza el sistema en un núcleo de dominio aislado, rodeado de puertos (interfaces) y adaptadores (implementaciones concretas para REST, colas de mensajes y bases de datos).
* **BD:** Base de Datos relacional (PostgreSQL).
* **CI/CD:** Integración Continua / Entrega Continua (*Continuous Integration / Continuous Delivery*).
* **Circuit Breaker:** Patrón de resiliencia que detecta fallos en llamadas externas y evita cascadas de error.
* **DAS:** Documento de Arquitectura de Software.
* **Message Broker:** Intermediario de mensajería utilizado para la comunicación asíncrona entre microservicios. En la implementación actual se usa AWS SNS como publicador y colas SQS como consumidores.
* **REST:** *Representational State Transfer* (Transferencia de Estado Representacional). Estilo arquitectural para APIs web.

## **Referencias**

| Documento | Versión | Fecha de la versión |
| :---- | :---- | :---- |
| Caso_FleetOps_Contexto_Negocio | 1.0 | 2026-I |
| Caso_FleetOps_Problemas.pdf | 1.0 | 2026-I |
| Caso_FleetOps_Procesos | 1.0 | 2026-I |
| Documento_4_FleetOps_Final | 1.0 | 2026-I |
| Pre_planificación_incidentes | 1.1 | 2026-I |

## **Vista Global**

El documento se organiza en las siguientes secciones:

* Sección 1 – Introducción: propósito, alcance, definiciones y referencias.
* Sección 2 – Macro Arquitectura: descripción de capas, metas y restricciones arquitectónicas con tablas de atributos de calidad observables y no observables.
* Sección 3 – Vista Física: infraestructura de contenedores, base de datos y bus de mensajería.
* Sección 4 – Vista Funcional o Lógica: componentes internos, casos de uso, integraciones y patrones aplicados.
* Sección 5 – Vista de Despliegue: nodos, CI/CD y stack tecnológico.

El microservicio adopta una arquitectura hexagonal (Ports and Adapters), organizada en tres zonas:

* **Núcleo de dominio:** contiene la lógica de negocio pura (gestión de incidentes, reglas de validación y construcción del agregado). No depende de ninguna tecnología externa.
* **Puertos de entrada (Driving Adapters):** adaptador REST API que recibe solicitudes de usuarios (conductores, coordinadores, administradores) a través del API Gateway.
* **Puertos de salida (Driven Adapters):** adaptador de BD (ORM Django → PostgreSQL) y adaptador de mensajería (productor SNS para fan-out hacia SQS y suscriptores externos).

# **Macro Arquitectura**

El microservicio de Incidentes adopta una arquitectura hexagonal (Ports and Adapters) dentro del ecosistema de microservicios de FleetOps. Esta arquitectura aísla el núcleo de dominio de las tecnologías externas, conectándose al mundo exterior mediante dos tipos de adaptadores:

* **REST API:** canal exclusivo de interacción con usuarios (conductores, coordinadores, administradores) a través del API Gateway.
* **Message Broker (SNS/SQS):** canal exclusivo de comunicación asíncrona con el ecosistema de microservicios. El servicio publica eventos y los consumidores externos reaccionan por sus propias colas.

Los patrones arquitectónicos complementarios son: Circuit Breaker (resiliencia en el adaptador REST de entrada), Repository Pattern sobre el adaptador de persistencia y BD relacional PostgreSQL. Los registros de incidentes son inmutables una vez creados

Flujo de dependencias en la arquitectura hexagonal:

* Adaptador REST (entrada) → Núcleo de dominio: el adaptador REST transforma la solicitud HTTP y llama al caso de uso correspondiente en el dominio.
* Núcleo de dominio → Adaptador BD (salida): el dominio persiste el incidente en PostgreSQL a través del puerto de repositorio, implementado con el ORM de Django.
* Núcleo de dominio → Adaptador de mensajería (salida): el dominio publica el evento al puerto de mensajería, implementado con SNS, al completar el registro del incidente.

## **Metas y Restricciones Arquitectónicas**

| Atributos de Calidad "Observables" |  |  |  |
| ----- | :---- | :---- | :---- |
| **Atributo de Calidad** | **Descripción** | **Tácticas / Patrón de Diseño** | **Donde se aplica** |
| **Disponibilidad** | Capacidad del sistema de estar operativo al ser requerido, manejando eficazmente las fallas que puedan afectar su funcionamiento. | Circuit Breaker sobre la llamada REST al microservicio de Vehículos. Manejo explícito de excepciones en la capa de aplicación y REST. | Endpoint de creación de incidentes y validación de placa. |
| **Trazabilidad** | Todo incidente queda registrado para consulta posterior por conductor, vehículo, tipo, gravedad o rango de fechas. | BD relacional exclusiva con registros de incidentes inmutables y campos de auditoría técnica (`created_at` y `updated_at`). | Persistencia en PostgreSQL y endpoints de consulta. |
| **Resiliencia** | Tolerancia a fallos en la comunicación con otros microservicios, sin afectar la operación principal del servicio de incidentes. | Circuit Breaker para la integración síncrona con Vehículos. Publicación asíncrona de eventos mediante SNS. La publicación fallida se registra, pero no bloquea el registro del incidente. | Validación de vehículo y publicación del evento de dominio. |
| **Seguridad** | Acceso controlado a los endpoints; datos de entrada validados en cada operación. | API Gateway como proxy centralizado: autenticación, autorización y control de tráfico. Validación de datos en la capa de API REST. | Todos los endpoints del microservicio expuestos vía API Gateway. |
| **Integridad de Datos** | Los datos de incidentes son consistentes y válidos en todo momento, incluso ante fallos parciales. | Validaciones en el serializer REST, validación de placa contra Vehículos, persistencia transaccional en PostgreSQL y pruebas unitarias. | Endpoint de creación y repositorio de incidentes. |
| **Despliegue Automatizado** | Cada cambio validado se despliega de forma automática y reproducible. | Pipeline CI/CD con GitHub Actions: build, pruebas unitarias, análisis estático (SonarCloud) y despliegue en contenedor Docker. | Repositorio GitHub del microservicio. Ambiente de integración continua. |

| Atributos de Calidad "No Observables" |  |  |  |
| ----- | :---- | :---- | :---- |
| **Atributo** | **Descripción** | **Tácticas / Patrón de Arquitectura** | **Donde se aplica** |
| **Modificabilidad** | Habilidad de realizar cambios futuros al sistema con bajo impacto en otros módulos (Bosch et al., 1999). | Arquitectura Hexagonal (Ports and Adapters): el núcleo de dominio es independiente de los adaptadores. Reemplazar REST por otro protocolo o cambiar de BD requiere solo cambiar el adaptador, sin tocar el dominio. | Toda la estructura del microservicio de incidentes. Interfaces de comunicación con otros microservicios. |
| **Mantenibilidad** | Capacidad de modificar el sistema de manera rápida y a bajo costo (Barbacci et al., 1995). | Código versionado en GitHub con ramas y Pull Requests. Análisis estático con SonarCloud. Pipeline CI/CD automatizado. Estandarización de nombres y estructura de código. | Repositorio GitHub. Pipeline de CI/CD con GitHub Actions. |
| **Escalabilidad** | Capacidad de ampliar el servicio para soportar el crecimiento de la flota sin degradación del rendimiento (Pressman, 2002). | Contenedores Docker: cada instancia es replicable horizontalmente. BD PostgreSQL independiente. API sin estado en la capa REST. | Contenedores Docker del microservicio. Base de datos PostgreSQL. |
| **Facilidad de Integración** | Capacidad de comunicarse con los microservicios de Vehículos, Mantenimiento y Asignaciones de forma desacoplada. | REST API estandarizada para usuarios. Mensajería asíncrona con SNS y colas SQS suscritas por otros servicios. API Gateway como punto único de entrada. | Canal REST con usuarios (conductores, coordinadores, administradores). Canal de mensajería con microservicios internos. |

### **Restricciones Técnicas**

* Arquitectura exclusivamente backend, sin capa de presentación propia.
* Arquitectura basada en microservicios con comunicación REST hacia usuarios y mensajería asíncrona (SNS/SQS) hacia otros microservicios.
* Base de datos relacional propia por microservicio (PostgreSQL). Los registros de incidentes son inmutables; no se actualiza su estado.
* Patrones obligatorios: Circuit Breaker y Message Broker.
* Gestión de versiones y CI/CD mediante GitHub y GitHub Actions.
* Despliegue en contenedores Docker.
* Framework Django REST Framework.
* Mensajería AWS SNS con suscriptores SQS.

# **Vista Física**

La vista física describe la distribución y despliegue del microservicio de Incidentes en infraestructura de contenedores. Cada componente se despliega de forma independiente para garantizar aislamiento, escalabilidad y tolerancia a fallos.

**Nodos físicos:**

* Contenedor Docker – Microservicio de Incidentes: ejecuta la aplicación Django REST Framework con la lógica de negocio y la API REST. Expuesto únicamente a través de la API Gateway.
* Contenedor Docker – PostgreSQL: base de datos relacional exclusiva del microservicio. Almacena los registros de incidentes (inmutables). Sin acceso externo directo.
* API Gateway: punto de entrada unificado que recibe las solicitudes REST de usuarios y las redirige al microservicio. Centraliza autenticación, autorización y control de tráfico.
* SNS (Message Broker): tópico de mensajería para la comunicación asíncrona. Recibe eventos publicados por el microservicio de Incidentes y los distribuye a los suscriptores externos mediante colas SQS.

Flujo de interacciones físicas:

1. El usuario (conductor/coordinador/administrador) envía una solicitud REST al API Gateway.
2. El API Gateway autentica/autoriza y redirige al contenedor del microservicio de Incidentes.
3. El microservicio procesa la solicitud, aplica la lógica de negocio y escribe el resultado en PostgreSQL.
4. Al persistir el incidente, el microservicio publica un evento `incident_registered` a SNS.
5. Los microservicios consumidores procesan el evento desde sus colas SQS y reaccionan según sus propias reglas.

Todos los contenedores se gestionan mediante Docker Compose o un orquestador compatible, garantizando portabilidad y reproducibilidad del entorno.

# **Vista Funcional o Lógica**

La Vista Funcional describe los componentes internos del microservicio de Incidentes, sus responsabilidades y las interacciones entre ellos y con los microservicios externos de la plataforma FleetOps.

## **Componentes Internos**

El microservicio se organiza en tres zonas de la arquitectura hexagonal:

**Núcleo de dominio (lógica de negocio pura):**

* Caso de uso – Registrar Incidente: valida la placa, persiste el registro y publica el evento `incident_registered`.
* Caso de uso – Consultar Incidentes: ejecuta las consultas filtradas por tipo, gravedad, conductor, placa o fecha.
* Caso de uso – Obtener Incidente por ID: recupera un incidente individual desde el repositorio.
* Reglas de negocio: valida tipos de incidente (`HUMANO` / `MECANICO`), gravedad (`LEVE` / `GRAVE`) y formato de placa.

**Adaptadores de entrada (Driving Adapters):**

* Adaptador REST API (Django REST Framework): recibe las solicitudes HTTP de usuarios a través del API Gateway y las traduce en llamadas a los casos de uso del dominio.

**Adaptadores de salida (Driven Adapters):**

* Adaptador de Repositorio (ORM Django → PostgreSQL): implementa el puerto de persistencia del dominio. Escribe los registros de incidentes en la BD. Los registros son inmutables una vez creados.
* Adaptador de Mensajería (SNS Publisher): implementa el puerto de mensajería del dominio. Publica los eventos al tópico para que los consumidores externos los procesen desde SQS.
* Adaptador HTTP de Vehículos (requests + pybreaker): valida la existencia de la placa mediante una llamada REST protegida por Circuit Breaker.

## **Casos de Uso / Historias de Usuario**

1. Como conductor, deseo registrar un incidente asociado a un vehículo y/o conductor, especificando la gravedad y detalles del evento.
2. Como administrador o coordinador, deseo acceder al registro histórico de incidentes, filtrables por vehículo, conductor, rango de fechas y gravedad.
3. Como sistema, deseo validar que la placa exista en el microservicio de Vehículos antes de persistir un incidente.
4. Como sistema, deseo que, al registrar un incidente, se publique un evento de dominio para que otros microservicios reaccionen según sus propias reglas.
5. Como conductor o coordinador, deseo consultar un incidente específico por su identificador único.

## **Integración con Otros Microservicios**

El microservicio de Incidentes se comunica con usuarios vía REST API y con otros microservicios exclusivamente mediante eventos publicados al Message Broker (SNS):

* Microservicio de Vehículos: el microservicio de Incidentes realiza una validación síncrona por REST para verificar que la placa exista. Esta es la única llamada REST directa entre microservicios, ademas consume el evento para evaluar sus propias reglas de disponibilidad.
* Microservicio de Mantenimiento: consume el evento publicado para iniciar sus propios flujos de revisión y reparación. La coordinación distribuida no está orquestada por este servicio en el código actual.
* Microservicio de Asignaciones: consume el evento para evaluar sus propias reglas de reasignación o notificación.

## **Patrones de Diseño Aplicados**

* API Gateway: centraliza seguridad, autenticación y enrutamiento del tráfico REST de usuarios.
* Circuit Breaker: protege la capa REST ante fallos o latencias excesivas al consultar Vehículos.
* Message Broker (SNS/SQS): desacopla el microservicio de Incidentes de los consumidores externos. La publicación fallida se registra, pero no cancela el registro ya persistido.
* BD Relacional: el incidente se persiste en PostgreSQL con campos de auditoría técnica (`created_at`, `updated_at`) y sin tabla de estado propia.

# **Vista de Despliegue**

La Vista de Despliegue describe cómo el microservicio de Incidentes se ejecuta y distribuye en nodos físicos o virtuales, y cómo se interconectan en el entorno de producción.

## **Nodos y Configuración**

* Nodo 1 – Microservicio de Incidentes: contenedor Docker ejecutando Django REST Framework. Se conecta al nodo de PostgreSQL para persistencia y a SNS para publicación de eventos.
* Nodo 2 – PostgreSQL: contenedor Docker dedicado exclusivamente a la persistencia de registros de incidentes del microservicio. Sin acceso externo directo. Los registros son inmutables.
* Nodo 3 – API Gateway: recibe todo el tráfico REST de usuarios y lo enruta al microservicio. Gestiona autenticación, autorización y control de tráfico.
* Nodo 4 – SNS/SQS: tópico y colas de mensajería para la comunicación asíncrona entre microservicios.

## **Desarrollo y CI/CD**

* Código versionado en GitHub con estrategia de ramas (main, develop, integrantes).
* Pull Requests obligatorios con revisión de código antes de merge a ramas principales.
* Pipeline CI/CD con GitHub Actions: build, ejecución de pruebas unitarias, análisis estático con SonarCloud y despliegue automático en ambiente de integración.
* Cobertura de pruebas unitarias obligatoria con umbral mínimo definido en el pipeline.

## **Riesgos y Deuda Técnica**

* Riesgo de inconsistencia eventual entre microservicios si falla la publicación del evento; mitigado con publicación best-effort, logs y reintentos a nivel de infraestructura.
* Complejidad en la coordinación distribuida; mitigada por mantener el núcleo de dominio aislado y por el uso de eventos de dominio simples.
* Dependencia del correcto levantamiento y rendimiento de SNS/SQS; requiere monitoreo activo y configuración ade
## **Riesgos y Deuda Técnica**

* Riesgo de inconsistencia eventual entre microservicios si falla la publicación del evento; mitigado con publicación best-effort, logs y reintentos a nivel de infraestructura.
* Complejidad en la coordinación distribuida; mitigada por mantener el núcleo de dominio aislado y por el uso de eventos de dominio simples.
* Dependencia del correcto levantamiento y rendimiento de SNS/SQS; requiere monitoreo activo y configuración adecuada de colas consumidoras.
* La integración rápida puede descuidar cobertura de pruebas; mitigado con umbrales de cobertura obligatorios en el pipeline CI/CD.cuada de colas consumidoras.
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
| **Message Broker** | AWS SNS / SQS |
| **Análisis de Código** | SonarCloud |
| **HTTP Client** | requests |
| **Circuit Breaker** | pybreaker |
| **SDK de Mensajería** | boto3 |

# **Modelo de Datos y Flujos de Trabajo**

Esta sección describe el modelo de base de datos del microservicio de Incidentes y los flujos de trabajo que se ejecutan ante cada tipo de evento.

## **Modelo de Base de Datos**

El microservicio de Incidentes posee su propia base de datos PostgreSQL exclusiva. La entidad principal es la tabla incidents, definida a continuación:

| Modelo de Base de Datos – Tabla: incidents |  |  |  |
| ----- | :---- | :---- | :---- |
| **Campo** | **Tipo de Dato** | **Restricción** | **Descripción** |
| **id** | VARCHAR(20) | PK, NOT NULL | Identificador único del incidente. Generado automáticamente con un prefijo legible. |
| **fecha_hora** | TIMESTAMP | NOT NULL | Fecha y hora exacta en que ocurrió el incidente. |
| **created_at** | TIMESTAMP | NOT NULL, AUTO | Fecha de creación del registro. |
| **updated_at** | TIMESTAMP | NOT NULL, AUTO | Fecha de última actualización técnica del registro. |
| **id_conductor** | VARCHAR(255) | NOT NULL | Identificador del conductor que reporta el incidente. No es FK física a otra base de datos. |
| **placa_vehiculo** | VARCHAR(20) | NOT NULL | Placa del vehículo involucrado. Validada contra el microservicio de Vehículos antes del registro. |
| **tipo_incidente** | ENUM | NOT NULL | Categoría del incidente. Valores permitidos: HUMANO | MECANICO. |
| **gravedad** | ENUM | NOT NULL | Nivel de gravedad del incidente. Valores permitidos: LEVE | GRAVE. |
| **descripcion** | TEXT | NOT NULL | Descripción detallada del incidente reportada por el conductor. |

Nota: los registros de incidentes son inmutables una vez creados; no se actualizan ni tienen campo de estado. Los campos id_conductor y placa_vehiculo no son claves foráneas directas a otras BDs (cada microservicio gestiona su propia BD). La validación de la placa se realiza en tiempo de solicitud consultando al microservicio de Vehículos antes de persistir el registro.

## **Flujos de Trabajo**

### **Flujo 1 – Validación de placa y registro del incidente**

Cuando un cliente (conductor, coordinador) envía una solicitud POST al REST API del microservicio de Incidentes, se ejecuta el siguiente flujo de validación previo al registro:

| Paso | Actor / Componente | Acción |
| :---: | :---- | :---- |
| 1 | API Gateway | Recibe la solicitud REST, autentica y autoriza al usuario. Redirige al microservicio de Incidentes. |
| 2 | Microservicio Incidentes | Recibe los datos del incidente (vehicle_id, driver_id, incident_type, severity, description, event_date). |
| 3 | Microservicio Incidentes → Microservicio Vehículos | Consulta REST (síncrona) al microservicio de Vehículos para verificar que la placa esté registrada en el sistema. Esta es la única llamada REST directa entre microservicios; está protegida con Circuit Breaker. |
| 4a | Microservicio Incidentes | Si la placa NO está registrada: retorna error HTTP 422 al cliente con mensaje "Placa no registrada en el sistema". No se persiste ningún dato. |
| 4b | Microservicio Incidentes | Si la placa SÍ está registrada: persiste el incidente (registro inmutable) en la BD PostgreSQL y continúa al Flujo 2. |

### **Flujo 2 – Publicación del evento de dominio**

Una vez validada la placa y persistido el incidente, el microservicio publica un evento genérico `incident_registered` al Message Broker (SNS).

| Paso | Actor / Componente | Acción |
| :---: | :---- | :---- |
| 1 | Microservicio Incidentes | Publica `incident_registered` con los datos serializados del incidente. |
| 2 | SNS | Distribuye el evento a los consumidores suscritos mediante SQS. |
| 3 | Microservicios consumidores | Ejecutan sus propias reglas de negocio de forma desacoplada. |

### **Flujo 3 – Consulta de incidentes por el Servicio de Reportes**

El Servicio de Reportes puede consultar la información de la BD de incidentes directamente a través de los endpoints REST del microservicio. Las consultas están protegidas por el API Gateway (autenticación y autorización de solo lectura para el rol de Reportes).

| Filtro de Consulta | Parámetro | Descripción |
| :---- | :---- | :---- |
| **Por tipo de incidente** | incident_type | Retorna todos los incidentes de tipo HUMANO o MECANICO. |
| **Por gravedad** | severity | Retorna todos los incidentes de gravedad LEVE o GRAVE. |
| **Por conductor** | driver_id | Retorna todos los incidentes reportados por un conductor específico. |
| **Por placa de vehículo** | vehicle_id | Retorna todos los incidentes asociados a una placa de vehículo específica. |
| **Por rango de fechas** | start_date / end_date | Retorna incidentes ocurridos dentro de un rango de fechas determinado. |
| **Combinación de filtros** | Múltiples parámetros | Los filtros anteriores pueden combinarse en una misma consulta para obtener resultados más específicos. |

El Servicio de Reportes accede a los datos directamente vía REST GET al microservicio de Incidentes; no tiene acceso directo a la BD PostgreSQL. Esto garantiza que toda consulta pase por la capa de seguridad del API Gateway y la lógica de autorización del microservicio.

## **Contratos HTTP Actuales**

| Operación | Método | Ruta |
| :---- | :---- | :---- |
| Crear incidente | POST | /api/incidents/create/ |
| Consultar incidentes | GET | /api/incidents/ |
| Consultar incidente por ID | GET | /api/incidents/{incident_id}/ |

## **Variables de Entorno Relevantes**

| Variable | Uso |
| :---- | :---- |
| DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT | Conexión a PostgreSQL |
| VEHICLES_API_URL | Base URL del microservicio de Vehículos |
| SNS_TOPIC_ARN | ARN del tópico SNS para publicación de eventos |
| AWS_REGION | Región AWS utilizada por el cliente SNS |
| DJANGO_SECRET_KEY | Clave secreta de Django |
| JWT_ALGORITHM / JWT_PUBLIC_KEY_PATH | Configuración de autenticación JWT |