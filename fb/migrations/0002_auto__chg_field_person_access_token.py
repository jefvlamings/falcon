# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Person.access_token'
        db.alter_column(u'fb_person', 'access_token', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Person.access_token'
        db.alter_column(u'fb_person', 'access_token', self.gf('django.db.models.fields.CharField')(default=None, max_length=30))

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
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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