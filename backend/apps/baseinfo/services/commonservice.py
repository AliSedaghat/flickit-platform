from django.db.models import F

from baseinfo.models.questionmodels import AnswerTemplate, OptionValue, Question, QuestionImpact
from baseinfo.models.assessmentkitmodels import MaturityLevel, AssessmentKit
from baseinfo.models.basemodels import AssessmentSubject, QualityAttribute, Questionnaire
from baseinfo.serializers import commonserializers

from baseinfo.services import assessmentkitservice

from django.core.exceptions import ObjectDoesNotExist


def check_subject_in_assessment_kit(assessment_kit_id, subject_id):
    if AssessmentKit.objects.filter(id=assessment_kit_id).filter(assessment_subjects=subject_id).exists():
        return AssessmentSubject.objects.get(id=subject_id)
    return False


def check_attributes_in_assessment_kit(assessment_kit_id, attribute_id):
    if AssessmentKit.objects.filter(id=assessment_kit_id).filter(
            assessment_subjects__quality_attributes=attribute_id).exists():
        return QualityAttribute.objects.get(id=attribute_id)
    return False


def check_maturity_level_in_assessment_kit(assessment_kit_id, maturity_level_id):
    if MaturityLevel.objects.filter(assessment_kit=assessment_kit_id).filter(id=maturity_level_id).exists():
        return MaturityLevel.objects.get(id=maturity_level_id)
    return False


def check_questionnaire_in_assessment_kit(assessment_kit_id, questionnaire_id):
    if Questionnaire.objects.filter(assessment_kit=assessment_kit_id).filter(id=questionnaire_id).exists():
        return Questionnaire.objects.get(id=questionnaire_id)
    return False


def check_question_in_assessment_kit(assessment_kit_id, question_id):
    if Question.objects.filter(id=question_id).filter(questionnaire__assessment_kit=assessment_kit_id).exists():
        return Question.objects.get(id=question_id)
    return False


def load_answer_tamplate(answer_tamplate_id) -> AnswerTemplate:
    try:
        return AnswerTemplate.objects.get(id=answer_tamplate_id)
    except AnswerTemplate.DoesNotExist as e:
        raise AnswerTemplate.DoesNotExist


def load_quality_attribute(quality_attribute_id) -> QualityAttribute:
    try:
        return QualityAttribute.objects.get(id=quality_attribute_id)
    except QualityAttribute.DoesNotExist as e:
        raise QualityAttribute.DoesNotExist


def load_question_impact(question_impact_id) -> QuestionImpact:
    try:
        return QuestionImpact.objects.get(id=question_impact_id)
    except QuestionImpact.DoesNotExist as e:
        raise QuestionImpact.DoesNotExist


def load_assessment_subject(assessment_subject_id) -> AssessmentSubject:
    try:
        return AssessmentSubject.objects.get(id=assessment_subject_id)
    except AssessmentSubject.DoesNotExist as e:
        raise AssessmentSubject.DoesNotExist


def get_option_value_with_answer_tamplate(answer_tamplate_id):
    answer_tamplate = load_answer_tamplate(answer_tamplate_id=answer_tamplate_id)
    result = OptionValue.objects.filter(option=answer_tamplate_id)
    return result


def get_assessment_subject_with_assessment_kit(assessment_kit_id):
    try:
        AssessmentKit.objects.get(id=assessment_kit_id)
    except AssessmentKit.DoesNotExist as e:
        return False
    result = AssessmentSubject.objects.filter(assessment_kit=assessment_kit_id)
    return result


def get_question_with_quality_attribute(quality_attribute_id):
    quality_attribute = load_quality_attribute(quality_attribute_id)
    result = Question.objects.filter(quality_attributes=quality_attribute_id)
    return result


def get_quality_attribute_with_assessment_subject(assessment_subject_id):
    assessment_subject = load_assessment_subject(assessment_subject_id)
    result = QualityAttribute.objects.filter(assessment_subject=assessment_subject_id)
    return result


def get_question_impact_with_id(question_impact_id):
    question_impact = load_question_impact(question_impact_id)
    result = QuestionImpact.objects.filter(id=question_impact_id)
    return result


def get_questions_with_assessmnet_kit_id(assessment_kit_id):
    try:
        AssessmentKit.objects.get(id=assessment_kit_id)
    except AssessmentKit.DoesNotExist as e:
        return False
    result = Question.objects.filter(questionnaire__assessment_kit=assessment_kit_id).order_by("id")
    return result


def get_answer_option_whit_id(answer_option_ids):
    answer_option_list = answer_option_ids.split(',')
    answer_option_list = [int(x) for x in answer_option_list if x.isdigit()]
    result = AnswerTemplate.objects.filter(id__in=answer_option_list)
    return result


def get_maturity_level_details(maturity_levels, quality_attributes_id):
    data = list()
    for level in maturity_levels:
        data_level = dict()
        data_level['id'] = level.id
        data_level['title'] = level.title
        data_level['index'] = level.value
        questions_count = QuestionImpact.objects.filter(maturity_level=level.id).filter(
            quality_attribute=quality_attributes_id).distinct().values('question__id').count()
        data_level['questions_count'] = questions_count
        data.append(data_level)
    return data


def get_questions_in_maturity_level(maturity_level, quality_attributes_id):
    data_questions = list()
    data = get_maturity_level_details([maturity_level], quality_attributes_id)[0]
    questions_impact = QuestionImpact.objects.filter(
        quality_attribute=quality_attributes_id).filter(maturity_level=maturity_level.id)
    questions = questions_impact.values("question__id", "question__title", "question__index",
                                        "question__may_not_be_applicable", "question__questionnaire__title", "weight")
    options = list(
        questions_impact.values("question__id", "option_values__value", "option_values__option__index",
                                "option_values__option__caption"))
    for question in questions:
        ids = 0
        data_question = dict()
        options_list = list()
        data_question["index"] = question["question__index"]
        data_question["title"] = question["question__title"]
        data_question["may_not_be_applicable"] = question["question__may_not_be_applicable"]
        data_question["weight"] = question["weight"]
        data_question["questionnaire"] = question["question__questionnaire__title"]
        for i in range(len(options)):
            option_values = {}
            if options[i]["question__id"] == question["question__id"]:
                option_values["index"] = options[i]["option_values__option__index"]
                option_values["title"] = options[i]["option_values__option__caption"]
                option_values["value"] = options[i]["option_values__value"]
                options_list.append(option_values)
            else:
                ids = i
                break
        options = options[ids:]
        data_question["option"] = options_list
        data_questions.append(data_question)

    data["questions"] = data_questions
    return data


def get_question_impacts_for_questionnaire(question_id, attributes):
    data = list()
    for attribute in attributes:
        data_attribute_list = dict()
        data_attribute = dict()
        data_attribute['id'] = attribute.id
        data_attribute['title'] = attribute.title
        affected_levels = list()
        impacts = attribute.question_impacts.filter(question=question_id)
        for impact in impacts:
            affected_level_data = dict()
            maturity_level_data = dict()
            maturity_level_data["id"] = impact.maturity_level.id
            maturity_level_data["index"] = impact.maturity_level.value
            maturity_level_data["title"] = impact.maturity_level.title
            affected_level_data["maturity_level"] = maturity_level_data
            affected_level_data["weight"] = impact.weight
            option_values_data = commonserializers.LoadOptionDetailsSerializer(impact.option_values, many=True).data

            affected_level_data["option_values"] = option_values_data
            affected_levels.append(affected_level_data)
        data_attribute["affected_levels"] = affected_levels
        data_attribute_list["attribute"] = data_attribute
        data.append(data_attribute_list)
    return data
