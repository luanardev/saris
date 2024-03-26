from django.http import HttpResponse
from django_renderpdf import helpers

class RenderPDFMixin:
    allow_force_html: bool = True
    prompt_download: bool = False
    download_name = None

    def get_download_name(self) -> str:
        return self.download_name


    def url_fetcher(self, url):
        return helpers.django_url_fetcher(url)
    

    def render_pdf(self, request, template, context) -> HttpResponse:
        response = HttpResponse(content_type="application/pdf")
        if self.prompt_download:
            response["Content-Disposition"] = 'attachment; filename="{}"'.format(
                self.get_download_name()
            )
        helpers.render_pdf(
            template=template,
            file_=response,
            url_fetcher=self.url_fetcher,
            context=context,
        )
        return response
    
