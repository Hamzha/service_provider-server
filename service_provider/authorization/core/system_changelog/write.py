from authorization.models.system_changelog import SystemChangelog


def create_system_changelog(action_performed, changed_in, changed_reference_id, description, created_at, created_by):
    try:
        result = SystemChangelog(action_performed=action_performed, changed_in=changed_in,
                                 changed_reference_id=changed_reference_id, description=description, created_at=created_at, created_by=created_by)
        result.save()
    except Exception:
        return False

def bulk_create_system_changelog(action_performed, changed_in, changed_reference_id, description, created_at, created_by):
    try:
        all_system_changelog = []
        for id in changed_reference_id:
            change_log = SystemChangelog(action_performed=action_performed, changed_in=changed_in,
                                    changed_reference_id=id, description=description, created_at=created_at, created_by=created_by)
            all_system_changelog.append(change_log)
        result =  SystemChangelog.objects.bulk_create(all_system_changelog)
        result.save()
    except Exception:
        return False