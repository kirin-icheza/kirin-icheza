#include <stdio.h>    
#include <sys/types.h>    
#include <sys/stat.h>    
#include <sys/ioctl.h>    
#include <fcntl.h>    
#include <unistd.h>    
#include "led_module.h"
#include <string.h>
#include <stdlib.h>

#define DEVICE_FILENAME  "/dev/simple"    

void ledControl(int pinNum, int value)
{
    int dev, ret;    
    ledCtl ledctl;

    memset(&ledctl, 0, sizeof(ledCtl));    
    int size = sizeof(ledctl);    
        
    printf( "device file open\n");     
    dev = open( DEVICE_FILENAME, O_RDWR|O_NDELAY );    
        
    if( dev >= 0 )
    {  
        ledctl.pin = pinNum;
        ledctl.funcNum = 1;   
        ledctl.act.on = value;
       
        /* 
        printf( "App : write something\n");    
        ret = write(dev, (char *)&ledCtl, size);    
        printf( "%s %dbytes\n", buf, ret );    
        
        printf( "App : read something\n");    
        ret = read(dev, buf2, 100 );    
        printf( "%s %dbytes\n", buf2, ret );    
        */
        printf( "ioctl function call\n");
        
        ret = ioctl(dev, MY_IOCSQSET, &ledctl );    
        printf( "ret = %d\n", ret );    

        ret = ioctl(dev, MY_IOCSQ_GPIO_SETFUNC);    
        printf( "ret = %d\n", ret );    

        ret = ioctl(dev, MY_IOCSQ_GPIO_ACTIVE);    
        printf( "ret = %d\n", ret );    
       
        printf( "device file close\n");    
        ret = close(dev);    
        printf( "ret = %d\n", ret );    
    }    
}
