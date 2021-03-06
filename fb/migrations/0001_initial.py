# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table(u'fb_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fb_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('relationship_status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('significant_other', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('progress', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'fb', ['Person'])

        # Adding model 'Relationship'
        db.create_table(u'fb_relationship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_people', to=orm['fb.Person'])),
            ('to_person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_people', to=orm['fb.Person'])),
        ))
        db.send_create_signal(u'fb', ['Relationship'])

        # Adding model 'Location'
        db.create_table(u'fb_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fb.Person'])),
            ('name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('travel_distance', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('hometown_distance', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'fb', ['Location'])


    def backwards(self, orm):
        # Deleting model 'Person'
        db.delete_table(u'fb_person')

        # Deleting model 'Relationship'
        db.delete_table(u'fb_relationship')

        # Deleting model 'Location'
        db.delete_table(u'fb_location')


    models = {
        u'fb.location': {
            'Meta': {'object_name': 'Location'},
            'hometown_distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fb.Person']"}),
            'travel_distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'fb.person': {
            'Meta': {'object_name': 'Person'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'progress': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'relationship_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to+'", 'symmetrical': 'False', 'through': u"orm['fb.Relationship']", 'to': u"orm['fb.Person']"}),
            'significant_other': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        u'fb.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'from_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_people'", 'to': u"orm['fb.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_people'", 'to': u"orm['fb.Person']"})
        }
    }

    complete_apps = ['fb']