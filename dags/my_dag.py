from airflow import DAG
from datetime import datetime
from random import randint

#importing operators
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator

# Python functions to be used in this DAG
def _training_model():
    return randint(1,100)

def _choose_best_model(ti):
    """
    ti = task instance
    
    ti.xcom_pull
    Pulls the return_value XCOM from a specified task_id in task_ids variable
        task_ids = arry;str; must be a specified task_id defined in this DAG
    """
    accuracies = ti.xcom_pull(task_ids=[
        'training_model_A',
        'training_model_B',
        'training_model_C'
    ])
    best_accuracy = max(accuracies)
    if (best_accuracy > 8):
        return 'accurate'
    return 'inaccurate'

with DAG("my_dag",start_date=datetime(2021, 1, 1),
    schedule_interval="@daily", catchup=False) as dag:
    # "my_dag" = DAG_ID *required
    # start_date = <datetime; when will the DAG first run/be scheduled by Airflow>
    # schedule_interval = <string; cron expression; for the frequency of running the DAG>
    # catchup = <Boolean; The scheduler, by default, will kick off a DAG Run for any interval that has not been run since the last execution date (or has been cleared)>
        
        # Sample PythonTask
        training_model_A = PythonOperator(
            task_id= "training_model_A",
            python_callable=_training_model
        )
        # variable = PythonOperator()
        # Within the operator (Python Operator)
        #   task_id = task name
        #   python_callable = python function to be run

        training_model_B = PythonOperator(
            task_id= "training_model_B",
            python_callable=_training_model
        )

        training_model_C = PythonOperator(
            task_id= "training_model_C",
            python_callable=_training_model
        )

        # Calling a Branch Python Operator
        #   Use this operator to execute a python operator to execute one task or another
        #   Callable function must return the taskid to operate

        choose_best_model = BranchPythonOperator(
            task_id="choose_best_model",
            python_callable = _choose_best_model
        )

        # Bash Operator
        #   Calling a bash task in Airflow

        accurate = BashOperator(
            task_id="accurate",
            bash_command="echo 'accurate'"
        )

        inaccurate = BashOperator(
            task_id="inaccurate",
            bash_command="echo 'inaccurate'"
        )

        # To Specify order in which tasks are executed
        # Use Bit Shift Operator

        # Downstream Task (>>)
        # Upstream Task (<<)
        # Group tasks together as a List ([Task A, Task B, Task C])
        
        [training_model_A, training_model_B, training_model_C] >> choose_best_model >> [accurate, inaccurate]