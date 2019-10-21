from django.db import models


class Ip(models.Model):
    # id = models.AutoField(primary_key=True)
    basename = models.CharField(max_length=8,unique=True,primary_key=True)
    ipaddr = models.GenericIPAddressField(default=u'127.0.0.1')
    ports = models.CharField(max_length=10,unique=True,null=True)
    ostype = models.CharField(max_length=10,default=u'client')
    rate = models.CharField(max_length=3, default=u'1s')
    status = models.CharField(max_length=3,default='OFF')
    # remark = models.TextField(max_length=50, blank=True, verbose_name=u'备注')

    def __unicode__(self):
        return u'%s - %s - %s' %(self.ipaddr, self.basename, self.ports )


class Datas(models.Model):
    id = models.AutoField(primary_key=True)
    basename = models.CharField('基站名', max_length=8 )
    lendata =models.SmallIntegerField('字节数',default=0 )
    utime = models.DateTimeField(auto_now=False)

    def __str__(self):
        return self.basename

class Monitor(models.Model):
    id = models.AutoField(primary_key=True)
    basename_e = models.CharField( max_length=8 )
    data_byte =models.SmallIntegerField(default=0 )
    p_time = models.DateTimeField(auto_now=False)

    def __str__(self):
        return self.basename_e