import datetime

from instance import scheduler

messages = [
    'Подниму сообщение, если вдруг оно укатилось. Тема реально интересная, сам недавно с этим разбирался.',
    'Понимаю, что можете быть заняты, но всё же интересно, что думаете.',
    'Ладно, больше не буду отвлекать. Если вдруг интересно, могу просто скинуть то, что сам недавно нашёл – штука, которая помогает с поиском. Без спама, просто вдруг пригодится. 😉'
]


async def follow_up_message(send_client, target_handler: str, message: str):
    try:
        await send_client.send_message(target_handler, message)
    except Exception as e:
        print(f"Ошибка при отправке follow‑up сообщения для {target_handler}: {e}")


def cancel_follow_ups(target_handler: str):
    """
    Ищет все задания, связанные с follow‑up для target_handler и удаляет их.
    """
    for job in scheduler.get_jobs():
        if job.id.startswith(f"followup_{target_handler}_"):
            try:
                scheduler.remove_job(job.id)
            except Exception as e:
                print(f"Ошибка при отмене follow‑up задачи {job.id} для {target_handler}: {e}")


async def delete_chat_task(send_client, target_handler: str):
    try:
        await send_client.delete_chat(target_handler)
    except Exception as e:
        print(f"Ошибка при удалении чата для {target_handler}: {e}")


def schedule_follow_ups(send_client, target_handler: str):
    """
    Отменяет существующие follow‑up задачи для target_handler и планирует новые с задержками 6, 24 и 48 часов.
    """
    cancel_follow_ups(target_handler)
    delays = [6, 24, 48]
    for delay, msg in zip(delays, messages):
        run_time = datetime.datetime.now() + datetime.timedelta(hours=delay)
        job_id = f"followup_{target_handler}_{delay}"
        scheduler.add_job(
            follow_up_message,
            'date',
            run_date=run_time,
            args=[send_client, target_handler, msg],
            id=job_id,
            replace_existing=True
        )


def schedule_delete_chat(send_client, target_handler: str):
    """
    Отменяет существующее задание удаления чата для target_handler (если есть) и планирует новое через 72 часа.
    """
    job_id = f"delete_{target_handler}"
    try:
        scheduler.remove_job(job_id)
    except Exception as e:
        pass
    run_time = datetime.datetime.now() + datetime.timedelta(hours=72)
    scheduler.add_job(
        delete_chat_task,
        'date',
        run_date=run_time,
        args=[send_client, target_handler],
        id=job_id,
        replace_existing=True
    )