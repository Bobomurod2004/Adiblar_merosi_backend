from rest_framework import serializers

from .models import (
    PracticeOption,
    PracticeQuestion,
    PracticeTest,
    ScholarshipApplication,
    ScholarshipProgram,
)


class ScholarshipProgramSerializer(serializers.ModelSerializer):
    requirements = serializers.SerializerMethodField()

    class Meta:
        model = ScholarshipProgram
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'monthly_amount',
            'requirements',
            'deadline',
            'is_open',
        )

    def get_requirements(self, obj):
        return obj.requirements_list


class ScholarshipApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipApplication
        fields = (
            'full_name',
            'email',
            'phone',
            'university',
            'study_year',
            'gpa',
            'motivation_letter',
            'portfolio_url',
        )

    def validate(self, attrs):
        request = self.context['request']
        program = self.context['program']

        if ScholarshipApplication.objects.filter(program=program, applicant=request.user).exists():
            raise serializers.ValidationError(
                "Ushbu stipendiyaga siz allaqachon ariza yuborgansiz."
            )

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        program = self.context['program']

        return ScholarshipApplication.objects.create(
            program=program,
            applicant=request.user,
            status='submitted',
            **validated_data,
        )


class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    program = ScholarshipProgramSerializer(read_only=True)

    class Meta:
        model = ScholarshipApplication
        fields = (
            'id',
            'program',
            'full_name',
            'email',
            'phone',
            'university',
            'study_year',
            'gpa',
            'motivation_letter',
            'portfolio_url',
            'status',
            'admin_notes',
            'decided_at',
            'created_at',
        )


class PracticeOptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeOption
        fields = ('id', 'option_text', 'order')


class PracticeQuestionPublicSerializer(serializers.ModelSerializer):
    options = PracticeOptionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = PracticeQuestion
        fields = ('id', 'prompt', 'order', 'options')


class PracticeTestListSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PracticeTest
        fields = (
            'id',
            'title',
            'slug',
            'topic',
            'duration_minutes',
            'level',
            'pass_percent',
            'questions_count',
            'starts_at',
            'expires_at',
        )


class PracticeTestDetailSerializer(serializers.ModelSerializer):
    questions = PracticeQuestionPublicSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = PracticeTest
        fields = (
            'id',
            'title',
            'slug',
            'topic',
            'description',
            'duration_minutes',
            'level',
            'pass_percent',
            'questions_count',
            'starts_at',
            'expires_at',
            'questions',
        )

    def get_questions_count(self, obj):
        return obj.questions.count()


class TestSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(min_value=1),
        help_text='question_id: option_id formatida yuboring',
    )
    time_spent_seconds = serializers.IntegerField(min_value=0, required=False)

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("Kamida bitta savolga javob yuboring.")
        return value
