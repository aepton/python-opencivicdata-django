from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.encoding import python_2_unicode_compatible

from .base import (OCDBase, LinkBase, OCDIDField, RelatedBase, RelatedEntityBase, MimetypeLinkBase,
                   IdentifierBase)
from .people_orgs import Organization
from .jurisdiction import LegislativeSession
from .. import common


@python_2_unicode_compatible
class Bill(OCDBase):
    id = OCDIDField(ocd_type='bill')
    legislative_session = models.ForeignKey(LegislativeSession, related_name='bills')
    identifier = models.CharField(max_length=100)

    title = models.TextField()

    from_organization = models.ForeignKey(Organization, related_name='bills', null=True)
    classification = ArrayField(base_field=models.TextField(), blank=True, default=list)      # check that array values are in enum?
    subject = ArrayField(base_field=models.TextField(), blank=True, default=list)

    def __str__(self):
        return '{} in {}'.format(self.identifier, self.legislative_session)

    class Meta:
        index_together = [
            ['from_organization', 'legislative_session', 'identifier'],
        ]


@python_2_unicode_compatible
class BillAbstract(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='abstracts')
    abstract = models.TextField()
    note = models.TextField(blank=True)
    date = models.TextField(max_length=10, blank=True)  # YYYY[-MM[-DD]]

    def __str__(self):
        return '{0} abstract'.format(self.bill.identifier)


@python_2_unicode_compatible
class BillTitle(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='other_titles')
    title = models.TextField()
    note = models.TextField(blank=True)

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.bill.identifier)


class BillIdentifier(IdentifierBase):
    bill = models.ForeignKey(Bill, related_name='other_identifiers')
    note = models.TextField(blank=True)


@python_2_unicode_compatible
class BillAction(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='actions')
    organization = models.ForeignKey(Organization, related_name='actions')
    description = models.TextField()
    date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
    classification = ArrayField(base_field=models.TextField(), blank=True, default=list)     # enum
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{0} action on {1}'.format(self.bill.identifier, self.date)


@python_2_unicode_compatible
class BillActionRelatedEntity(RelatedEntityBase):
    action = models.ForeignKey(BillAction, related_name='related_entities')

    def __str__(self):
        return '{0} related to {1}'.format(self.entity_name, self.action)


@python_2_unicode_compatible
class RelatedBill(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='related_bills')
    related_bill = models.ForeignKey(Bill, related_name='related_bills_reverse', null=True)
    identifier = models.CharField(max_length=100)
    # not a FK in case we don't know the session yet
    legislative_session = models.CharField(max_length=100)
    relation_type = models.CharField(max_length=100, choices=common.BILL_RELATION_TYPE_CHOICES)

    def __str__(self):
        return 'relationship of {} to {} ({})'.format(self.bill, self.related_bill,
                                                      self.relation_type)


@python_2_unicode_compatible
class BillSponsorship(RelatedEntityBase):
    bill = models.ForeignKey(Bill, related_name='sponsorships')
    primary = models.BooleanField(default=False)
    classification = models.CharField(max_length=100)   # enum?

    def __str__(self):
        return '{} ({}) sponsorship of {}'.format(self.name, self.entity_type, self.bill)


@python_2_unicode_compatible
class BillDocument(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='documents')
    note = models.CharField(max_length=300)
    date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]

    def __str__(self):
        return '{0} document of {1}'.format(self.date, self.bill)


@python_2_unicode_compatible
class BillVersion(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='versions')
    note = models.CharField(max_length=300)
    date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]

    def __str__(self):
        return '{0} version of {1}'.format(self.date, self.bill)


@python_2_unicode_compatible
class BillDocumentLink(MimetypeLinkBase):
    document = models.ForeignKey(BillDocument, related_name='links')

    def __str__(self):
        return '{0} for {1}'.format(self.url, self.document.bill)


@python_2_unicode_compatible
class BillVersionLink(MimetypeLinkBase):
    version = models.ForeignKey(BillVersion, related_name='links')

    def __str__(self):
        return '{0} for {1}'.format(self.url, self.version)


class BillSource(LinkBase):
    bill = models.ForeignKey(Bill, related_name='sources')
