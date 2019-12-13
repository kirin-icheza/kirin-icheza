obj-m+=led_dev.o  
    
ARCH :=arm  
PWD := $(shell pwd)  
     
all:  
	make -C /lib/modules/$(shell uname -r)/build/ M=$(PWD) ARCH=$(ARCH) modules  
demo:
	sudo gcc -c -fPIC led_module.c
	sudo gcc -shared -o led_module.so led_module.o 
clean:  
	make -C /lib/modules/$(shell uname -r)/build/ M=$(PWD) ARCH=$(ARCH) clean
	rm -rf simple
