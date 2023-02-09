from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from baseinfo.models.profilemodels import AssessmentProfile, ProfileTag
from baseinfo.models.basemodels import AssessmentSubject, Questionnaire, QualityAttribute
from baseinfo.models.metricmodels import AnswerTemplate, MetricImpact, Metric
from baseinfo.imagecomponent.models import QualityAttributeImage, SubjectImage, ProfileImage
    
class ProfileImageFormInline(admin.TabularInline):
     model = ProfileImage
     fields= ['image']
     extra = 0

@admin.register(AssessmentProfile)
class AssessmentProfileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['code', 'title']
    list_display = ['code', 'title', 'is_default']
    list_editable = ['title']
    list_per_page = 10
    inlines= [ProfileImageFormInline]

class SubjectImageFormInline(admin.TabularInline):
     model = SubjectImage
     fields= ['image']
     extra = 0

@admin.register(AssessmentSubject)
class AssessmentSubjectAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    autocomplete_fields = ['questionnaires']
    search_fields = ['code', 'title', 'assessment_profile']
    fields = ['code', 'title', 'description', 'assessment_profile', 'questionnaires', 'index']
    list_display = ['code', 'title', 'subject_questionnaires', 'assessment_profile']
    list_editable = ['title']
    list_per_page = 10
    inlines= [SubjectImageFormInline]

    def subject_questionnaires(self, obj):
        return "\n".join([att.title for att in obj.questionnaires.all()])


@admin.register(Questionnaire)
class QuestionnaireAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['code', 'title', 'assessment_profile']
    fields = ['code', 'title', 'description', 'assessment_profile', 'index']
    list_display = ['code', 'title', 'assessment_profile']
    list_editable = ['title']
    list_per_page = 10


class MetricImpactFormInline(admin.TabularInline):
     model = MetricImpact
     fields= ['level', 'quality_attribute']
     autocomplete_fields= ['quality_attribute']
     extra = 0

class AnswerTemplateFormInline(admin.TabularInline):
     model = AnswerTemplate
     fields= ['caption', 'value', 'index']
     extra = 0

class QualityAttributeImageFormInline(admin.TabularInline):
     model = QualityAttributeImage
     fields= ['image']
     extra = 0

@admin.register(Metric)
class MetricAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    autocomplete_fields = ['questionnaire']
    search_fields = ['title']
    list_filter = ['questionnaire', 'last_modification_date']
    list_display = ['title', 'questionnaire', 'quality_attributes_metric']
    list_per_page = 10
    inlines = [MetricImpactFormInline, AnswerTemplateFormInline]

    def quality_attributes_metric(self, obj):
        return "\n".join([att.title for att in obj.quality_attributes.all()])

@admin.register(QualityAttribute)
class QualityAttributeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    fields = ['code', 'title', 'description', 'assessment_subject', 'index']
    search_fields = ['title', 'assessment_subject']
    list_display = ['code', 'title', 'assessment_subject']
    list_editable = ['title']
    list_per_page = 10
    inlines= [QualityAttributeImageFormInline]


@admin.register(ProfileTag)
class TagAdmin(admin.ModelAdmin):
    fields = ['code', 'title']
    search_fields = ['title', 'code']
    list_display = ['code', 'title', 'profiles_tag']
    list_editable = ['title']
    list_per_page = 10

    def profiles_tag(self, obj):
        return "\n".join([profile.title for profile in obj.profiles.all()])