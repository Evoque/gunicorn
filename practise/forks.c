#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

void fork7()
{
    if (fork() == 0)
    {
        /* Child */
        printf("Terminating Child, PID = %d\n", getpid());
        exit(0);
    }
    else
    {
        printf("Running Parent, PID = %d\n", getpid());
        while (1)
            ; /* Infinite loop */
    }
}

/**
 * Demonstrating of nonterminating child.
 * Child still running even though parent terminated
 * Must kill explicitly
 */
void fork_nonterminating_child()
{
    /* Child */
    if (fork() == 0)
    {
        printf("Running Child, PID = %d \n", getpid());
        while (1) /* Infinite loop */
            ;
    }
    else 
    {
        printf("Terminating Parent, PID = %d \n", getpid());
        exit(0);
    }
}

/**
 * Synchronizing with 
 */
void fork_sync_reap()
{
    int child_status;

    if (fork() == 0)
    {
        printf("HC: hello from child, PID=%d \n", getpid());
        exit(0);
    }
    else
    {
        printf("HP: hello from parent, PID=%d \n", getpid());
        int r_pid = wait(&child_status);
        printf("CT: child has terminated, RID=%d, Status=%d \n", r_pid, child_status);
    }
    printf("Bye\n");
}


int main(int argc, char *argv[])
{
    // fork7();
    // fork_nonterminating_child();
    fork_sync_reap();
    return 0;
}