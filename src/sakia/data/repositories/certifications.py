import attr

from ..entities import Certification


@attr.s(frozen=True)
class CertificationsRepo:
    """The repository for Communities entities.
    """
    _conn = attr.ib()  # :type sqlite3.Connection
    _primary_keys = (Certification.currency, Certification.certified,
                     Certification.certifier, Certification.block,)

    def insert(self, certification):
        """
        Commit a certification to the database
        :param sakia.data.entities.Certification certification: the certification to commit
        """
        certification_tuple = attr.astuple(certification)
        values = ",".join(['?'] * len(certification_tuple))
        self._conn.execute("INSERT INTO certifications VALUES ({0})".format(values), certification_tuple)

    def update(self, certification):
        """
        Update an existing certification in the database
        :param sakia.data.entities.Certification certification: the certification to update
        """
        updated_fields = attr.astuple(certification, filter=attr.filters.exclude(*CertificationsRepo._primary_keys))
        where_fields = attr.astuple(certification, filter=attr.filters.include(*CertificationsRepo._primary_keys))
        self._conn.execute("""UPDATE certifications SET
                           ts=?,
                           signature=?,
                           written_on=?
                           WHERE
                           currency=? AND
                           certifier=? AND
                           certified=? AND
                           block=?""",
                           updated_fields + where_fields)

    def get_one(self, **search):
        """
        Get an existing certification in the database
        :param dict search: the criterions of the lookup
        :rtype: sakia.data.entities.Certification
        """
        filters = []
        values = []
        for k, v in search.items():
            filters.append("{k}=?".format(k=k))
            values.append(v)

        request = "SELECT * FROM certifications WHERE {filters}".format(filters=" AND ".join(filters))

        c = self._conn.execute(request, tuple(values))
        data = c.fetchone()
        if data:
            return Certification(*data)

    def get_all(self, **search):
        """
        Get all existing certification in the database corresponding to the search
        :param dict search: the criterions of the lookup
        :rtype: sakia.data.entities.Certification
        """
        filters = []
        values = []
        for k, v in search.items():
            value = v
            filters.append("{key} = ?".format(key=k))
            values.append(value)

        request = "SELECT * FROM certifications WHERE {filters}".format(filters=" AND ".join(filters))

        c = self._conn.execute(request, tuple(values))
        datas = c.fetchall()
        if datas:
            return [Certification(*data) for data in datas]
        return []

    def get_latest_sent(self, currency, pubkey):
        """
        Get latest sent certification
        :param str currency:
        :param str pubkey:
        :return:
        :rtype: sakia.data.entities.Certification
        """
        request = """SELECT * FROM certifications
                  WHERE currency=? AND certifier=?
                  ORDER BY ts DESC
                  LIMIT 1"""
        c = self._conn.execute(request, (currency, pubkey))
        data = c.fetchone()
        if data:
            return Certification(*data)

    def drop(self, certification):
        """
        Drop an existing certification from the database
        :param sakia.data.entities.Certification certification: the certification to update
        """
        where_fields = attr.astuple(certification, filter=attr.filters.include(*CertificationsRepo._primary_keys))
        self._conn.execute("""DELETE FROM certifications
                              WHERE
                              currency=? AND
                              certifier=? AND
                              certified=? AND
                              block=?""", where_fields)
