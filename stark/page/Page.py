
class Pagination(object):
    def __init__(self,current_page,all_count,base_url,query_params, per_page=20, pager_page_count=11):
        '''
        分页初始化
        :param current_page: 当前页
        :param all_count: 数据的总数
        :param page_count: 页数总计
        :param base_url:基础URL(当前请求路径)
        :param query_params:QueryDict对象，内部含所有当前URL的原条件
        :param per_page: 每页显示数据条数
        :param pager_page_count:页面上的页码数量
        :return:
        '''
        self.base_url = base_url
        try:
            self.current_page = int(current_page)
            if self.current_page < 1:
                raise Exception()
        except Exception as e:
            self.current_page = 1

        self.query_params = query_params
        self.all_count = all_count
        self.per_page = per_page
        self.pager_page_count = pager_page_count
        page_count,b = divmod(self.all_count,self.per_page)
        if b != 0:
            page_count += 1
        self.page_count = page_count
        half_pager_page_count = int(self.pager_page_count/2)
        self.half_pager_page_count = half_pager_page_count

    @property
    def start(self):
        '''
        数据获取值起始索引
        :return:
        '''
        return (self.current_page-1)*self.per_page
    @property
    def end(self):
        '''
        数据获取值结束索引
        :return:
        '''
        return self.current_page*self.per_page

    def page_html(self):
        '''
        生成分页HTML
        :return:
        '''
        if self.page_count<self.pager_page_count:
            start_page = 1
            end_page = self.page_count
        else:
            if self.current_page <= self.half_pager_page_count:
                start_page = 1
                end_page = self.pager_page_count
            else:
                if self.current_page+self.half_pager_page_count > self.page_count:
                    end_page = self.page_count
                    start_page = self.page_count - self.pager_page_count + 1
                else:
                    start_page = self.current_page - self.half_pager_page_count
                    end_page = self.current_page + self.half_pager_page_count
        page_list = []
        if self.current_page <= 1:
            prev = "<li><a href='#'>上一页</a></li>"
        else:
            self.query_params['page'] = self.current_page - 1
            prev = '<li><a href="%s?%s">上一页</a></li>' % (self.base_url, self.query_params.urlencode())
        page_list.append(prev)
        for i in range(start_page, end_page + 1):
            self.query_params['page'] = i
            if self.current_page == i:
                tpl = '<li class="active"><a href="%s?%s">%s</a></li>' % (
                    self.base_url, self.query_params.urlencode(), i,)
            else:
                tpl = '<li><a href="%s?%s">%s</a></li>' % (self.base_url, self.query_params.urlencode(), i,)
            page_list.append(tpl)

        if self.current_page >= self.page_count:
            nex = '<li><a href="#">下一页</a></li>'
        else:
            self.query_params['page'] = self.current_page + 1
            nex = '<li><a href="%s?%s">下一页</a></li>' % (self.base_url, self.query_params.urlencode(),)
        page_list.append(nex)
        page_str = "".join(page_list)
        return page_str