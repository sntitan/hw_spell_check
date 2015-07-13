#include <stdio.h>
#include "stdlib.h"

/*
"This is c comment"
*/

// "This is cpp comment"

// haha

#define TEST_MACRO(a) \
do {\
	printf("%d\r\n",a);\
}while(0)

int main()
{
	char* pstr = "Hello, gug\r\n";
	char *ptmp = "hahahah", *pstr_2line = "hello \
				the second line\r\n";	
    char* /*just for test*/ a = "abd"; //this is test
    char* b = "ccc"; /* test comments //haha
    char* c = "ddd";
*/
	printf("debug: pstr %s\r\n", pstr);
	printf("debug: pstr_2line: %s\r\n", pstr_2line);
	printf("debug: pstr_2line: %s, %s\r\n", "abc", "bcd");
    printf("哈喽大家好\r\n")
	return 0;
}
