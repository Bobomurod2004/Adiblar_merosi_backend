import logging

import requests
from django.conf import settings
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils import timezone
from .models import PracticeQuestion, PracticeTest, ScholarshipProgram, TestAttempt
from .serializers import (
    PracticeTestDetailSerializer,
    PracticeTestListSerializer,
    ScholarshipApplicationCreateSerializer,
    ScholarshipApplicationSerializer,
    ScholarshipProgramSerializer,
    TestSubmitSerializer,
)

logger = logging.getLogger(__name__)


def resolve_ai_answer(message: str) -> str:
    message_lower = message.lower()

    if 'muqimiy' in message_lower:
        return (
            "Muqimiy ijodida xalqona ruh, ijtimoiy tanqid va ma'rifatparvarlik "
            "asosiy yo'nalishlardan hisoblanadi."
        )

    if 'qahhor' in message_lower:
        return (
            "Abdulla Qahhor nasrida ixcham uslub, kuchli xarakter yaratish va "
            "psixologik chuqurlik alohida o'rin tutadi."
        )

    if 'stipendiya' in message_lower:
        return (
            "Stipendiya uchun odatda test natijalari, o'zlashtirish ko'rsatkichi "
            "va motivatsion xat talab qilinadi."
        )

    if 'asar' in message_lower:
        return (
            "Asarlar bo'limida adiblar kesimida filtrlab o'qishingiz mumkin. "
            "Qiziqqan adibni aytsangiz, tavsiya beraman."
        )

    return (
        "Savolingiz qiziqarli. Hozircha qisqa javob berdim, keyingi bosqichda "
        "AI model bilan chuqurroq javob beradigan tizim ulaymiz."
    )


def build_chat_messages(message: str, history: list | None = None):
    messages = [
        {
            'role': 'system',
            'content': (
                "Siz 'Adiblar Merosi' platformasi uchun AI yordamchisiz. "
                "Javoblarni o'zbek tilida, qisqa va aniq bering."
            ),
        }
    ]

    for item in (history or [])[-8:]:
        role = str(item.get('role', '')).strip()
        content = str(item.get('content', '')).strip()
        if role in {'user', 'assistant'} and content:
            messages.append({'role': role, 'content': content})

    messages.append({'role': 'user', 'content': message})
    return messages


def try_openai_answer(message: str, history: list | None = None):
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    model = getattr(settings, 'OPENAI_CHAT_MODEL', 'gpt-4.1-mini')

    if not api_key:
        return None

    payload = {
        'model': model,
        'messages': build_chat_messages(message, history),
        'temperature': 0.4,
    }

    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=20,
        )
        response.raise_for_status()

        data = response.json()
        choice = (data.get('choices') or [{}])[0]
        content = (choice.get('message') or {}).get('content')
        if content:
            return str(content).strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning('AI provider call failed: %s', exc)

    return None


class ScholarshipListView(generics.ListAPIView):
    serializer_class = ScholarshipProgramSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ScholarshipProgram.objects.filter(is_active=True, is_open=True).order_by('deadline')


class ScholarshipApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        program = get_object_or_404(
            ScholarshipProgram,
            slug=slug,
            is_active=True,
            is_open=True,
        )

        serializer = ScholarshipApplicationCreateSerializer(
            data=request.data,
            context={'request': request, 'program': program},
        )
        serializer.is_valid(raise_exception=True)
        application = serializer.save()

        response_data = ScholarshipApplicationSerializer(application).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class TestListView(generics.ListAPIView):
    serializer_class = PracticeTestListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return (
            PracticeTest.objects.filter(
                Q(is_active=True),
                Q(starts_at__isnull=True) | Q(starts_at__lte=now),
                Q(expires_at__isnull=True) | Q(expires_at__gt=now),
            )
            .annotate(questions_count=Count('questions'))
            .order_by('title')
        )


class TestDetailView(generics.RetrieveAPIView):
    serializer_class = PracticeTestDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        now = timezone.now()
        return PracticeTest.objects.filter(
            Q(is_active=True),
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(expires_at__isnull=True) | Q(expires_at__gt=now),
        ).prefetch_related(
            Prefetch(
                'questions',
                queryset=PracticeQuestion.objects.order_by('order').prefetch_related('options'),
            )
        )


class TestSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        test = get_object_or_404(PracticeTest, slug=slug, is_active=True)

        serializer = TestSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data['answers']
        time_spent_seconds = serializer.validated_data.get('time_spent_seconds')

        questions = list(test.questions.prefetch_related('options').all())
        question_map = {question.id: question for question in questions}
        total_questions = len(question_map)

        normalized_answers = {}
        correct_answers = 0

        for question_id_raw, option_id in answers.items():
            try:
                question_id = int(question_id_raw)
            except (TypeError, ValueError):
                continue

            question = question_map.get(question_id)
            if not question:
                continue

            selected_option = None
            for option in question.options.all():
                if option.id == option_id:
                    selected_option = option
                    break

            is_correct = bool(selected_option and selected_option.is_correct)
            if is_correct:
                correct_answers += 1

            normalized_answers[str(question_id)] = {
                'selected_option_id': selected_option.id if selected_option else None,
                'is_correct': is_correct,
            }

        score_percent = round((correct_answers / total_questions * 100) if total_questions else 0, 2)

        attempt = TestAttempt.objects.create(
            test=test,
            user=request.user if request.user.is_authenticated else None,
            total_questions=total_questions,
            correct_answers=correct_answers,
            score_percent=score_percent,
            time_spent_seconds=time_spent_seconds,
            answers_data=normalized_answers,
        )

        return Response(
            {
                'attempt_id': attempt.id,
                'test': test.title,
                'total_questions': total_questions,
                'answered_questions': len(normalized_answers),
                'correct_answers': correct_answers,
                'score_percent': float(attempt.score_percent),
                'pass_percent': test.pass_percent,
                'passed': float(attempt.score_percent) >= test.pass_percent,
            }
        )


class AIChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = str(request.data.get('message', '')).strip()
        history = request.data.get('history') or []

        if not message:
            return Response(
                {'detail': "message maydoni bo'sh bo'lmasligi kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_answer = try_openai_answer(message, history)
        if ai_answer:
            return Response({'message': ai_answer, 'source': 'openai'})

        return Response({'message': resolve_ai_answer(message), 'source': 'rule-based'})


from django.http import JsonResponse

class DebugMediaView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        import os
        search_dirs = [
            '/opt/render/project/src/media',
            '/opt/render/project/src/backend/media',
            '/var/data/media',
        ]
        
        result = {}
        for directory in search_dirs:
            if os.path.exists(directory):
                files = []
                for root, dirs, filenames in os.walk(directory):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, directory)
                        size_kb = round(os.path.getsize(full_path) / 1024, 2)
                        files.append(f"{rel_path} ({size_kb} KB)")
                result[directory] = files
            else:
                result[directory] = "directory does not exist"
                
        # Also print base media settings
        from django.conf import settings
        result["settings"] = {
            "MEDIA_ROOT": getattr(settings, "MEDIA_ROOT", "not set"),
            "MEDIA_URL": getattr(settings, "MEDIA_URL", "not set"),
            "SERVE_MEDIA": getattr(settings, "SERVE_MEDIA", "not set"),
            "DEBUG": getattr(settings, "DEBUG", "not set"),
        }
        
        return JsonResponse(result, safe=False)
