from platformio.managers.platform import PlatformBase

class Picorv32Platform(PlatformBase):

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_dynamic_options(result)
        else:
            for key, value in result.items():
                result[key] = self._add_dynamic_options(result[key])
            return result

    def _add_dynamic_options(self, board):
        # upload protocols
        if not board.get("upload.protocols", []):
            board.manifest['upload']['protocols'] = ["serial"]
        if not board.get("upload.protocol", ""):
            board.manifest['upload']['protocol'] = "serial"

        # debug tools
        debug = board.manifest.get("debug", {})
        non_debug_protocols = ["serial"]
        supported_debug_tools = [
            "jlink",
            "gd-link",
            # "ft2232",  # duplicate of sipeed-rv-debugger
            "sipeed-rv-debugger",
            "altera-usb-blaster",
            "um232h",
            "rv-link"
        ]

        upload_protocol = board.manifest.get("upload", {}).get("protocol")
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        upload_protocols.extend(supported_debug_tools)
        if upload_protocol and upload_protocol not in upload_protocols:
            upload_protocols.append(upload_protocol)
        board.manifest['upload']['protocols'] = upload_protocols

        if "tools" not in debug:
            debug['tools'] = {}


        board.manifest['debug'] = debug
        return board
