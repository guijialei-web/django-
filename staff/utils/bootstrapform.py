from django import forms
class BootStrapModelForm(forms.ModelForm):
    '''验证方式1'''


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # 循环modelform中的每个字段，给每个字段的插件设置
        for name,field in self.fields.items():
            # 字段中有属性，保留原来的属性，没有属性，才添加
            if field.widget.attrs:
                field.widget.attrs['class']='form-control'
                field.widget.attrs['placeholder']=field.label

            else:
                field.widget.attrs={"class":"form-control","placeholder":field.label}
    '''验证方式2'''



class BootStrapForm(forms.Form):
    '''验证方式1'''


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # 循环modelform中的每个字段，给每个字段的插件设置
        for name,field in self.fields.items():
            # 字段中有属性，保留原来的属性，没有属性，才添加
            if field.widget.attrs:
                field.widget.attrs['class']='form-control'
                field.widget.attrs['placeholder']=field.label

            else:
                field.widget.attrs={"class":"form-control","placeholder":field.label}
    '''验证方式2'''