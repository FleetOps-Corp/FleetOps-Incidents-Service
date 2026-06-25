"""Unit tests for Django incident repository adapter."""

from datetime import datetime

from incidents.domain.models import (
    Incident,
    IncidentSeverity,
    IncidentType,
    PlateNumber,
)
from incidents.infrastructure.adapters.persistence import (
    incident_repository as repository_module,
)
from incidents.infrastructure.adapters.persistence.incident_repository import (
    DjangoIncidentRepository,
)


class FakeQuerySet(list):
    def filter(self, **kwargs):
        items = self
        for field, value in kwargs.items():
            if field.endswith("__gte"):
                attribute_name = field[:-5]
                items = [
                    item for item in items if getattr(item, attribute_name) >= value
                ]
            elif field.endswith("__lte"):
                attribute_name = field[:-5]
                items = [
                    item for item in items if getattr(item, attribute_name) <= value
                ]
            else:
                items = [item for item in items if getattr(item, field) == value]
        return FakeQuerySet(items)


class FakeIncidentORM:
    DoesNotExist = type("DoesNotExist", (Exception,), {})
    objects = None

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.fecha_hora = kwargs["fecha_hora"]
        self.id_conductor = kwargs["id_conductor"]
        self.placa_vehiculo = kwargs["placa_vehiculo"]
        self.tipo_incidente = kwargs["tipo_incidente"]
        self.gravedad = kwargs["gravedad"]
        self.descripcion = kwargs["descripcion"]
        self.created_at = kwargs.get("created_at", datetime(2026, 6, 1, 10, 0, 0))
        self.updated_at = kwargs.get("updated_at", datetime(2026, 6, 1, 11, 0, 0))
        self.saved = False

    def save(self):
        self.saved = True


class FakeManager:
    def __init__(self, items):
        self.items = FakeQuerySet(items)

    def get(self, **kwargs):
        for item in self.items:
            if all(getattr(item, key) == value for key, value in kwargs.items()):
                return item
        raise FakeIncidentORM.DoesNotExist()

    def all(self):
        return FakeQuerySet(self.items)

    def filter(self, **kwargs):
        return self.items.filter(**kwargs)


class TestDjangoIncidentRepository:
    def setup_method(self):
        self.repository = DjangoIncidentRepository()
        self.original_incident_orm = repository_module.IncidentORM
        repository_module.IncidentORM = FakeIncidentORM

    def teardown_method(self):
        repository_module.IncidentORM = self.original_incident_orm

    def _incident(self):
        return Incident(
            id="INC-20260601-abcd",
            id_conductor="driver-1",
            placa_vehiculo=PlateNumber("ABC-1234"),
            fecha_hora=datetime(2026, 6, 1, 10, 30, 0),
            tipo_incidente=IncidentType.HUMANO,
            gravedad=IncidentSeverity.GRAVE,
            descripcion="Desc",
            created_at=datetime(2026, 6, 1, 10, 31, 0),
            updated_at=datetime(2026, 6, 1, 10, 32, 0),
        )

    def _orm_item(
        self,
        incident_id="INC-20260601-abcd",
        plate="ABC-1234",
        driver="driver-1",
        tipo="HUMANO",
        gravedad="GRAVE",
    ):
        return FakeIncidentORM(
            id=incident_id,
            fecha_hora=datetime(2026, 6, 1, 10, 30, 0),
            id_conductor=driver,
            placa_vehiculo=plate,
            tipo_incidente=tipo,
            gravedad=gravedad,
            descripcion="Desc",
            created_at=datetime(2026, 6, 1, 10, 31, 0),
            updated_at=datetime(2026, 6, 1, 10, 32, 0),
        )

    def test_save_persists_orm_object(self):
        incident = self._incident()

        saved = self.repository.save(incident)

        assert saved is incident

    def test_find_by_id_returns_incident(self):
        FakeIncidentORM.objects = FakeManager([self._orm_item()])

        result = self.repository.find_by_id("INC-20260601-abcd")

        assert result is not None
        assert result.id == "INC-20260601-abcd"
        assert result.get_plate_str() == "ABC-1234"

    def test_find_by_id_returns_none_when_missing(self):
        FakeIncidentORM.objects = FakeManager([])

        result = self.repository.find_by_id("missing")

        assert result is None

    def test_find_all_maps_all_records(self):
        FakeIncidentORM.objects = FakeManager(
            [self._orm_item(), self._orm_item(incident_id="INC-20260601-efgh")]
        )

        result = self.repository.find_all()

        assert len(result) == 2
        assert result[0].id == "INC-20260601-abcd"
        assert result[1].id == "INC-20260601-efgh"

    def test_find_by_placa_filters_records(self):
        FakeIncidentORM.objects = FakeManager(
            [
                self._orm_item(),
                self._orm_item(incident_id="INC-20260601-efgh", plate="XYZ-9999"),
            ]
        )

        result = self.repository.find_by_placa("ABC-1234")

        assert len(result) == 1
        assert result[0].get_plate_str() == "ABC-1234"

    def test_find_by_conductor_filters_records(self):
        FakeIncidentORM.objects = FakeManager(
            [
                self._orm_item(),
                self._orm_item(incident_id="INC-20260601-efgh", driver="driver-2"),
            ]
        )

        result = self.repository.find_by_conductor("driver-1")

        assert len(result) == 1
        assert result[0].id_conductor == "driver-1"

    def test_find_by_date_range_filters_records(self):
        first = self._orm_item()
        second = self._orm_item(incident_id="INC-20260601-efgh")
        second.fecha_hora = datetime(2026, 6, 3, 10, 30, 0)
        FakeIncidentORM.objects = FakeManager([first, second])

        result = self.repository.find_by_date_range(
            datetime(2026, 6, 1, 0, 0, 0),
            datetime(2026, 6, 2, 0, 0, 0),
        )

        assert len(result) == 1
        assert result[0].id == "INC-20260601-abcd"

    def test_find_by_filters_applies_all_conditions(self):
        FakeIncidentORM.objects = FakeManager(
            [
                self._orm_item(),
                self._orm_item(
                    incident_id="INC-20260601-efgh",
                    plate="XYZ-9999",
                    driver="driver-2",
                    tipo="MECANICO",
                    gravedad="LEVE",
                ),
            ]
        )

        result = self.repository.find_by_filters(
            tipo_incidente="HUMANO",
            gravedad="GRAVE",
            placa="ABC-1234",
            id_conductor="driver-1",
            fecha_desde=datetime(2026, 6, 1, 0, 0, 0),
            fecha_hasta=datetime(2026, 6, 2, 0, 0, 0),
        )

        assert len(result) == 1
        assert result[0].id == "INC-20260601-abcd"

    def test_orm_to_domain_converts_model(self):
        orm_item = self._orm_item()

        result = self.repository._orm_to_domain(orm_item)

        assert result.id == orm_item.id
        assert result.placa_vehiculo == PlateNumber("ABC-1234")
        assert result.tipo_incidente == IncidentType.HUMANO
        assert result.gravedad == IncidentSeverity.GRAVE
