from rest_framework.response import Response


class WakkaResponse(Response):

    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        """
        Restructuring the data to be returned in the response
        Schema: {
            "data": data,
            "status": status
        }"""
        if status:
            actual_data = data
            data = {"data": actual_data, "status": status}
            print("-" * 10, "DEBUG", "-" * 10)
            print(data)
        super().__init__(data, status, template_name, headers, exception, content_type)
