# SakshamAI workflow contracts

FastAPI owns authorization and business rules. n8n invokes only internal, authenticated workflow endpoints using `N8N_INTERNAL_SECRET`.

| Workflow | Event | Application endpoint | Outcome |
|---|---|---|---|
| 01_document_processing | `document.uploaded` | `POST /api/v1/documents` | extract, chunk, status update |
| 02_quiz_generation | `quiz.generation.requested` | `POST /api/v1/documents/{id}/generate-quiz` | review-required question set |
| 03_question_validation | `quiz.generated` | `PATCH /api/v1/questions/{id}` | trainer approval gate |
| 04_competency_analysis | `assessment.completed` | `POST /api/v1/attempts/{id}/submit` | evidence and score update |
| 05_recommendation_generation | `competency.updated` | `GET /api/v1/recommendations/me` | re-ranked pathway |
| 06_igot_course_sync | scheduled | integration adapter | sandbox / production sync log |
| 07_nssta_training_sync | scheduled | training programme adapter | programme refresh |
| 08_learning_completion | `course.completed` | learning progress endpoint | competency evidence |
| 09_notification_handler | `notification.created` | notifications endpoint | in-app delivery |

Production workflow JSON is deliberately not fabricated: import definitions only after the internal webhook URLs and authentication mechanism are configured.
