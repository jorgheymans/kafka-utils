import logging

from .cluster_info.display import display_assignment_changes
from .cluster_info.util import (
    get_reduced_proposed_plan,
    confirm_execution,
    proposed_plan_json,
)
from .util import KafkaInterface

_log = logging.getLogger('kafka-cluster-manager')


# Execute or display cluster-topology in zookeeper
def execute_plan(params):
    # Get final-proposed-plan
    result = get_reduced_proposed_plan(
        params['initial_plan'],
        params['curr_plan'],
        params['max_actions'],
    )
    apply = params['apply']
    no_confirm = params['no_confirm']
    # Valid plan found, Execute or display the plan
    log_only = False if apply and not no_confirm or not apply else True
    if result:
        # Display plan only if user-confirmation is required
        display_assignment_changes(result[1], result[2], result[3], log_only)

        to_execute = False
        proposed_plan = result[0]
        if apply:
            if no_confirm:
                to_execute = True
            else:
                if confirm_execution():
                    to_execute = True
        # Execute proposed-plan
        if to_execute:
            _log.info('Executing Proposed Plan')
            kafka = KafkaInterface(params['script_path'], params['no_script'])
            kafka.execute_plan(
                proposed_plan,
                params['zk'],
                params['brokers'],
                params['topics'],
            )
        else:
            _log.info('Proposed Plan won\'t be executed.')
        # Export proposed-plan to json file
        if params['proposed_plan_file']:
            proposed_plan_json(proposed_plan, params['proposed_plan_file'])
    else:
        # No new-plan
        msgStr = 'No topic-partition layout changes proposed.'
        if log_only:
            _log.info(msgStr)
        else:
            print(msgStr)
    return
