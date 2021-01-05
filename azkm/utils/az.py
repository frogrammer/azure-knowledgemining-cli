"""az cli utility library."""
from azure.cli.core import get_default_cli as az


def run_command(*cmd: tuple, verbose=False):
    """Run an az cli command.

    Args:
        command (str): cli command

    Returns:
        dict: result of command
    """
    if not verbose and '--output' not in cmd:
        cmd = cmd + ('--output', 'none')
    cli = az()
    cli.invoke(cmd)
    if cli.result.error:
        raise cli.result.error
    
    return cli.result.result

def logged_in() -> bool:
    """Check if logged in to az cli.

    Returns:
        bool: logged_in
    """
    try:
        res = run_command('account', 'list')
        return len(res) > 0
    except Exception as e:
        return False

def create_sp(name: str):
    sp = run_command('ad', 'sp', 'create-for-rbac', '--name', name)
    query = "[?appId=='{0}']|[0]".format(sp['appId'])
    full_sp = run_command('ad' , 'sp', 'list', '--show-mine', '--query', query)
    sp['objectId'] = full_sp['objectId']
    return sp

def delete_sp(name: str):
    return run_command('ad', 'sp', 'delete', name)
    