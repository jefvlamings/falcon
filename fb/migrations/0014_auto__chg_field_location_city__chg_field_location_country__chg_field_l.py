# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Location.city'
        db.alter_column(u'fb_location', 'city', self.gf('django.db.models.fields.CharField')(max_length=191, null=True))

        # Changing field 'Location.country'
        db.alter_column(u'fb_location', 'country', self.gf('django.db.models.fields.CharField')(max_length=191, null=True))

        # Changing field 'Location.fb_id'
        db.alter_column(u'fb_location', 'fb_id', self.gf('django.db.models.fields.CharField')(max_length=191, null=True))

        # Changing field 'Location.postal_code'
        db.alter_column(u'fb_location', 'postal_code', self.gf('django.db.models.fields.CharField')(max_length=191, null=True))

        # Changing field 'Person.fb_id'
        db.alter_column(u'fb_person', 'fb_id', self.gf('django.db.models.fields.CharField')(max_length=191, null=True))

        # Changing field 'Post.fb_id'
        db.alter_column(u'fb_post', 'fb_id', self.gf('django.db.models.fields.CharField')(max_length=191, null=True))

    def backwards(self, orm):

        # Changing field 'Location.city'
        db.alter_column(u'fb_location', 'city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Location.country'
        db.alter_column(u'fb_location', 'country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Location.fb_id'
        db.alter_column(u'fb_location', 'fb_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Location.postal_code'
        db.alter_column(u'fb_location', 'postal_code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Person.fb_id'
        db.alter_column(u'fb_person', 'fb_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Post.fb_id'
        db.alter_column(u'fb_post', 'fb_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    models = {
        u'fb.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '191', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '191', 'null': 'True', 'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'max_length': '191', 'null': 'True', 'blank': 'True'}),
            'hometown_distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fb.Person']"}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '191', 'null': 'True', 'blank': 'True'}),
            'travel_distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'fb.person': {
            'Meta': {'object_name': 'Person'},
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'max_length': '191', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'relationship_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to+'", 'symmetrical': 'False', 'through': u"orm['fb.Relationship']", 'to': u"orm['fb.Person']"}),
            'significant_other': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        u'fb.post': {
            'Meta': {'object_name': 'Post'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'max_length': '191', 'null': 'True', 'blank': 'True'}),
            'from_person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fb.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like_count': ('django.db.models.fields.IntegerField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'fb.progress': {
            'Meta': {'object_name': 'Progress'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percentage': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fb.Person']"})
        },
        u'fb.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'from_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_people'", 'to': u"orm['fb.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mutual_friend_count': ('django.db.models.fields.IntegerField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'to_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_people'", 'to': u"orm['fb.Person']"})
        }
    }

    complete_apps = ['fb']