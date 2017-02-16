from .traced_map import TracedMap


def cast_field_to_rvar(rvar_key, value):
    """
    Returns a field value cast to the rvar schema
    TODO: evaluate need for more formatting here
    """
    return str(value)


def cast_rvar_to_field(field_key, value):
    """
    Returns a field value cast from the rvar schema
    TODO: evaluate need for more formatting here
    """
    return str(value)


class FormMapper(object):
    """
    Uses TracedMaps to expose a field store to rvar reading and writing.
    Allows children to provide attributes to generate read/write maps per year.
    Caches maps on init according to year.
    Formats read output to rvars and write output to fields.
    """

    # Children implement field <-> rvar mapping by providing these attributes.
    # Functions should be decorated with @trace_map_func
    _READ_DICTS_BY_YEAR = {}
    _READ_FUNCS_BY_YEAR = {}
    _WRITE_DICTS_BY_YEAR = {}
    _WRITE_FUNCS_BY_YEAR = {}

    @classmethod
    def fields_read(cls, year):
        """
        Get all fields used to generate rvars.
        """
        return cls.__read_map(year).input_keys()

    @classmethod
    def rvars_generated(cls, year):
        """
        Get all rvars generated from fields.
        """
        return cls.__read_map(year).output_keys()

    @classmethod
    def rvars_used(cls, year):
        """
        Get all rvars written to fields.
        """
        return cls.__write_map(year).input_keys()

    @classmethod
    def fields_written(cls, year):
        """
        Get all fields written from rvars.
        """
        return cls.__write_map(year).output_keys()

    @classmethod
    def __read_map(cls, year):
        """
        Returns TracedMap that converts fields to rvars
        """
        return TracedMap(
            _dict=cls._READ_DICTS_BY_YEAR.get(year),
            formatter=cast_field_to_rvar,
            funcs=cls._READ_FUNCS_BY_YEAR.get(year),
        )

    @classmethod
    def __write_map(cls, year):
        """
        Returns TracedMap that converts rvars to fields
        """
        return TracedMap(
            _dict=cls._WRITE_DICTS_BY_YEAR.get(year),
            formatter=cast_rvar_to_field,
            funcs=cls._WRITE_FUNCS_BY_YEAR.get(year),
        )

    def __init__(self, year):
        """
        Caches a local copy of read and write maps according to year.
        """
        self._read_map = self.__read_map(year)
        self._write_map = self.__write_map(year)

    def _read_store(self):
        """
        Read stored field data for output mapping.
        Child class must implement.
        """
        raise NotImplementedError

    def _write_store(self, data):
        """
        Store mapped field data.
        Child class must implement.
        """
        raise NotImplementedError

    def read_rvars(self):
        """
        Apply the read map to stored field data and return rvars.
        """
        return self._read_map.map(self._read_store())

    def write_rvars(self, data):
        """
        Apply the write map to input rvars and store as fields.
        """
        self._write_store(self._write_map.map(data))
