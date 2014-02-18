/* NSGA-II GAUncert problem definition

   See http://www.iitk.ac.in/kangal/codes.shtml to obtain a copy of NSGA-II.
   Replace the provided 'problemdef.c' with this file before compilation.
   Read 'nsga2-readme.md' file for more details.
*/

#include <stdio.h>
#define GAUNCERT_COMMAND_BUFFER 512

const char* GAUNCERT_COMMAND = "mpiexec python main.py";

extern int nreal;
extern int nbin;
extern int nobj;
extern int ncon;

void test_problem(double *xreal, double *xbin, int **gene, double *obj, double *constr)
{
	/* Construct the gauncert command line and arguments */
	char command[GAUNCERT_COMMAND_BUFFER];
	char arg[GAUNCERT_COMMAND_BUFFER];
	int index;

	strncpy( command, GAUNCERT_COMMAND, GAUNCERT_COMMAND_BUFFER );

	for(index = 0; index < nreal; index++)
	{
		snprintf(arg, GAUNCERT_COMMAND_BUFFER, " --real %f", xreal[index]);
		strncat( command, arg, GAUNCERT_COMMAND_BUFFER - strlen(command) );
	}

	for(index = 0; index < nbin; index++)
	{
		snprintf(arg, GAUNCERT_COMMAND_BUFFER, " --bin %d", xbin[index]);
		strncat( command, arg, GAUNCERT_COMMAND_BUFFER - strlen(command) );
	}

	printf("GAUncert command:\n%s\n", command);

	/* Execute gauncert */
	FILE* pGAUncert;
	pGAUncert = (FILE*)popen(command,"r");
    if(pGAUncert == NULL)
	{
		printf("Could not run command: '%s'\n", command);
		exit(1);
	}
	
	/* Print the output from gauncert */
	int c;
	while((c = fgetc(pGAUncert)) != EOF)
	{
		putchar(c);
	}

	/* Make sure gauncert finished properly */
	int status;
	wait(&status);
	if(status != 0)
	{
		printf("Command failed: '%s'\n", command);
		exit(1);
	}

	/* Read objective and constraint values from output/ga.output file */
	FILE* pGAResults;
	pGAResults = (FILE*)fopen("output/ga.outputs", "r");
	if(pGAResults == NULL)
	{
		printf("Could not open 'output/ga.outputs'\n");
		exit(1);
	}

	char readRubbish[256];
	for(index = 0; index < nobj; index++)
	{
		fscanf(pGAResults, "%s%lf", readRubbish, &(obj[index]));
		printf("obj %d %f\n", index, obj[index]);
	}

	for(index = 0; index < ncon; index++)
	{
		fscanf(pGAResults, "%s%lf", readRubbish, &(constr[index]));
		printf("constr %d %f\n", index, constr[index]);
	}

    return;
}