import os
import sys


class Texture(object):
    """
    @type file_path: str
    @type origin: (float, float, float)
    @type stretch: (float, float, float)
    @type turbulence: (float, float, float)
    """
    def __init__(self):
        self.file_path = None
        self.origin = (0.0, 0.0, 0.0)
        self.stretch = (1.0, 1.0, 1.0)
        self.turbulence = (0.0, 0.0, 0.0)

    def read(self, map_statement, texture_directory=None):
        """

        @type map_statement: str
        @type texture_directory: str
        """
        tmp = map_statement.rsplit(' ', 1)
        if len(tmp) == 1:
            file_name = tmp[0]
        else:
            options, file_name = tmp
            while options.startswith('-'):
                if options.startswith('-o'):
                    key, u, v, w, options = options.split(' ', 4)
                    self.origin = (float(u), float(v), float(w))
                elif options.startswith('-s'):
                    key, u, v, w, options = options.split(' ', 4)
                    self.stretch = (float(u), float(v), float(w))
                elif options.startswith('-t'):
                    key, u, v, w, options = options.split(' ', 4)
                    self.turbulence = (float(u), float(v), float(w))
                else:
                    key, value, options = options.split(' ', 2)
        if texture_directory:
            self.file_path = os.path.join(texture_directory, file_name)

    def to_stream(self, stream):
        # stream.write("-o {} ".format(self.origin))
        # stream.write("-s {} ".format(self.stretch))
        # stream.write("-t {} ".format(self.turbulence))
        stream.write("{}\n".format(self.file_path))


class Material(object):
    """

    Color and  illumination
    # @type Ka:
    # @type Kd:
    # @type Ks:
    # @type Tf:
    # @type illum: int, glass 4, 9  Transparency 6, 7
    @type d: float
    # @type Ns:
    # @type sharpness:
    # @type Ni:

    Texture map
    @type map_Ka: Texture
    @type map_Kd: Texture
    # @type map_Ks:
    # @type map_Ns:
    # @type map_d:
    # @type disp:
    # @type decal:
    # @type bump:

    Reflection map
    # @type refl:
    """
    def __init__(self):
        self.d = 1.0  # 0: transparent
        self.map_Ka = None
        self.map_Kd = None

    def read(self, statement_lines, texture_directory=None):
        """

        @type statement_lines: list[str]
        @type texture_directory: str
        """
        for line in statement_lines:
            if ' ' in line:
                key, data_string = line.split(' ', 1)
            else:
                key, data_string = line, None
            if key == 'map_Ka':
                self.map_Ka = Texture()
                self.map_Ka.read(data_string, texture_directory)
            elif key == 'map_Kd':
                self.map_Kd = Texture()
                self.map_Kd.read(data_string, texture_directory)
            elif key == 'd':
                if data_string.startswith('-'):
                    self.d = float(data_string.rsplit(' ', 1)[1])
                else:
                    self.d = float(data_string)
            elif key == 'Tr':
                if data_string.startswith('-'):
                    self.d = 1 - float(data_string.rsplit(' ', 1)[1])
                else:
                    self.d = 1 - float(data_string)

    def get_texture(self):
        """

        @rtype: Texture
        """
        texture = self.map_Kd or self.map_Ka
        if texture is None:
            return None
        return texture

    def to_stream(self, stream):
        stream.write("  d {}\n".format(self.d))
        if self.map_Ka:
            stream.write("  map_Ka ".format(self.d))
            self.map_Ka.to_stream(stream)
        if self.map_Kd:
            stream.write("  map_Kd ".format(self.d))
            self.map_Kd.to_stream(stream)


class MtlReader(object):
    """
    A Minimalistic reader since I do not care about anything but texture

    newmtl Inner_Wall
        map_Ka bMOinnerwall.jpg
        map_Kd bMOinnerwall.jpg

        @type _materials: dict[str, Material]
    """
    def __init__(self):
        self._materials = {}
        self._texture_directory = "."

    def read_stream(self, input_stream, texture_directory="."):
        self._materials = {}
        self._texture_directory = texture_directory
        statement_lines = None
        material_name = ""
        for line in input_stream:
            line = line.strip()
            if line.startswith('#') or len(line) == 0:
                continue
            if line.startswith("newmtl"):
                if statement_lines:
                    self._materials[material_name] = Material()
                    self._materials[material_name].read(statement_lines, texture_directory)
                del statement_lines
                statement_lines = []
                material_name = line.split(' ', 1)[1]
            else:
                statement_lines.append(line)
        # read last material
        if statement_lines:
            self._materials[material_name] = Material()
            self._materials[material_name].read(statement_lines, texture_directory)

    def search_file(self, file_name_prefix):
        if "EXPORT" in file_name_prefix:
            file_name_prefix = file_name_prefix.split("EXPORT")[0]
        results = []
        for item in os.listdir(self._texture_directory):
            entry = item
            if "EXPORT" in entry:
                entry = item.split("EXPORT")[0]
            file_path = os.path.join(self._texture_directory, item)
            if entry.startswith(file_name_prefix) and os.path.isfile(file_path):
                results.append(item)
        if len(results) == 1:
            return results[0]
        return None
        # elif len(results) == 0:
        #     raise RuntimeError("Could not reconstruct texture file: {}".format(file_name_prefix))
        # else:
        #     raise RuntimeError("Could not reconstruct texture file, multiple hits found: {}".format(file_name_prefix))

    def reconstruct_mtl(self, input_stream, texture_directory="."):
        success_failure = [0, 0]
        self._materials = {}
        self._texture_directory = texture_directory
        for line in input_stream:
            line = line.strip()
            if line.startswith('#') or len(line) == 0:
                continue
            if not line.startswith("usemtl"):
                continue
            # todo: think of better way of dealing with odd export file material names
            material_name = line.split(' ', 1)[1]
            if "EXPORT" in material_name:
                material_name = material_name.split("EXPORT")[0]
            self._materials[material_name] = Material()
            file_name = self.search_file(material_name)
            if file_name is None:
                success_failure[1] += 1
                continue

            success_failure[0] += 1
            statement_lines = ["map_Ka {}".format(file_name)]
            self._materials[material_name].read(statement_lines, self._texture_directory)
        return success_failure

    def read(self, file_path, texture_directory=None):
        """

        @type file_path: str
        @type texture_directory: str
        @return:
        """
        assert os.path.exists(file_path), "Bad file path: {}".format(file_path)
        if texture_directory is None:
            texture_directory = os.path.dirname(file_path)
        success_failure = None
        # print(file_path)
        with open(file_path) as input_stream:
            if file_path.lower().endswith('.mtl'):
                self.read_stream(input_stream, texture_directory)
            elif file_path.lower().endswith('.obj'):
                success_failure = self.reconstruct_mtl(input_stream, texture_directory)
        return success_failure

    def get_material(self, material_name):
        """

        @rtype: Material
        """
        if material_name not in self._materials:
            return None
        return self._materials[material_name]

    def validate_textures(self):
        """

        @rtype: bool
        """
        for material_name, material in self._materials.items():
            texture = material.get_texture()
            if texture is None:
                continue
            file_path = texture.file_path
            if file_path is None:
                continue
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return False
        return True

    def to_stream(self, stream=None):
        if stream is None:
            stream = sys.stdout
        for material_name, material in self._materials.items():
            stream.write("newmtl {}\n".format(material_name))
            material.to_stream(stream)

    def to_stdout(self):
        self.to_stream(sys.stdout)
