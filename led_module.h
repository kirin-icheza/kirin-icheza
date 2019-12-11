#ifndef __SIMPLE__
#define __SIMPLE__

typedef struct _action{
    int on;
}action;

typedef struct _ledCtl{
    int pin;
    int funcNum;
    action act;
}__attribute__((packed))ledCtl;

#define MY_IOC_MAGIC 'c'

#define MY_IOCSQSET _IOW(MY_IOC_MAGIC, 0, ledCtl)
#define MY_IOCSQ_GPIO_SETFUNC _IO(MY_IOC_MAGIC, 1)
#define MY_IOCSQ_GPIO_ACTIVE _IO(MY_IOC_MAGIC, 2)

#define MY_IOC_MAXNR 3

#endif
