import sys
import os
from .defaultreader import DefaultReader


class MeshGroup(object):
    """
    # group name
        g [group name]
    # Vertices
        v 0.123 0.234 0.345 1.0
    # Texture coordinates
        vt 0.500 1 [0]
    # Vertex normals
        vn 0.707 0.000 0.707
    # Parameter space vertices
        vp 0.310000 3.210000 2.100000
    # Polygonal face element
        f 6/4/1 3/5/3 7/6/5
    # usemtl Material__3

    @type _material_library_file_path: str
    @type _tmp_material: str
    @type _vertex_indices: list[list[int, int, int]]
    @type _texture_indices: list[list[int, int, int]]
    @type _normal_indices: list[list[int, int, int]]
    @type _use_material: dict[str, list[int]]
    """
    def __init__(self, material_library_file_path=None):
        """
        @type material_library_file_path: str
        """
        self._material_library_file_path = material_library_file_path
        self._tmp_material = None
        self._vertex_indices = []
        self._texture_indices = []
        self._normal_indices = []
        self._use_material = {None: []}

    def __iter__(self):
        """
        access to block config from the class

        @rtype:
        """
        for face_element in self._vertex_indices:
            yield face_element

    def items_vertex(self):
        for element in self._vertex_indices:
            yield element

    def items_texture(self):
        for element in self._texture_indices:
            yield element

    def items_normal(self):
        for element in self._normal_indices:
            yield element

    def parse_f(self, line):
        vertex_indice = []
        texture_indice = []
        normal_indice = []
        for entry in line.split(' '):
            values = entry.split('/')
            vertex_indice.append(int(values[0]))
            if len(values) > 1:
                try:
                    texture_indice.append(int(values[1]))
                except ValueError:
                    pass
                if len(values) > 2:
                    try:
                        normal_indice.append(int(values[2]))
                    except ValueError:
                        pass
        self._vertex_indices.append(vertex_indice)
        if len(texture_indice):
            self._texture_indices.append(texture_indice)
        if len(normal_indice):
            self._normal_indices.append(normal_indice)
        self._use_material[self._tmp_material].append(len(self._vertex_indices))

    def parse_usemtl(self, line):
        """
        @type line: str
        """
        self._tmp_material = line
        self._use_material[self._tmp_material] = []

    def has_triangular_facets(self):
        if len(self._vertex_indices) == 0:
            return False
        return len(self._vertex_indices[0]) == 3


class MeshObject(object):
    """
    # o object name
    # mtllib Scaffold.mtl
    # g group name

    @type _groups: dict[str, MeshGroup]
    @type _tmp_material_library_file_path: str
    @type _vertices: list[list[float, float, float, float]]
    @type _texture_coordinates: list[list[float, float, float]]
    @type _vertex_normals: list[list[float, float, float]
    @type _parameter_space_vertices: list[list[int, int, int]]
    """
    def __init__(self, material_library_file_path=None):
        """
        """
        self._groups = {}
        self._tmp_material_library_file_path = material_library_file_path
        self._tmp_material = None
        self._vertices = []
        self._texture_coordinates = []
        self._vertex_normals = []
        self._parameter_space_vertices = []

    def parse_g(self, line):
        """
        @type line: str
        @rtype: MeshGroup
        """
        assert line not in self._groups, "Groups are not unique: {}".format(line)
        self._groups[line] = MeshGroup(self._tmp_material_library_file_path)
        return self._groups[line]

    def parse_v(self, line):
        """
        @type line: str
        """
        values = [float(value) for value in line.split(' ')]
        self._vertices.append(values)

    def parse_vt(self, line):
        """
        @type line: str
        """
        values = [float(value) for value in line.split(' ')]
        self._texture_coordinates.append(values)

    def parse_vn(self, line):
        """
        @type line: str
        """
        values = tuple([float(value) for value in line.split(' ')])
        self._vertex_normals.append(values)

    def parse_vp(self, line):
        """
        @type line: str
        """
        values = [int(value) for value in line.split(' ')]
        self._parameter_space_vertices.append(values)

    def parse_mtllib(self, line):
        """
        @type line: str
        """
        self._tmp_material_library_file_path = line

    def get_facets(self):
        """

        @rtype: collections.Iterable[((float, float, float), (float, float, float), (float, float, float))]
        """
        for name, group in self._groups.items():
            for indice in group.items_vertex():
                yield (
                    self._vertices[indice[0]-1],
                    self._vertices[indice[1]-1],
                    self._vertices[indice[2]-1])

    def get_texture_facets(self):
        """

        @rtype: collections.Iterable[((float, float, float), (float, float, float), (float, float, float))]
        """
        for name, group in self._groups.items():
            for indice in group.items_texture():
                yield (
                    self._texture_coordinates[indice[0]-1],
                    self._texture_coordinates[indice[1]-1],
                    self._texture_coordinates[indice[2]-1])

    def get_normals(self):
        """

        @rtype: collections.Iterable[((float, float, float), (float, float, float), (float, float, float))]
        """
        for name, group in self._groups.items():
            for indice in group.items_normal():
                yield (
                    self._vertex_normals[indice[0]-1],
                    self._vertex_normals[indice[1]-1],
                    self._vertex_normals[indice[2]-1])

    def has_triangular_facets(self):
        return all([group.has_triangular_facets() for name, group in self._groups.items()])


class ObjReader(DefaultReader):
    """
    @type _objects: dict[str, MeshObject]
    @type _tmp_material_library_file_path: str
    """
    def __init__(self):
        self._objects = {}
        self._tmp_material_library_file_path = None

    def read(self, file_path):
        self._objects = {}
        self._tmp_material_library_file_path = None
        current_object = None
        current_group = None
        with open(file_path) as input_stream:
            for line in input_stream:
                if line.startswith('#'):
                    continue
                line_split = line.rstrip().split(' ', 1)
                if len(line_split) == 1:
                    sys.stderr.write("[ObjReader] WARNING: Bad line: {}\n".format(line_split[0]))
                    continue
                key, data = line_split
                key = key.lower()
                if key == 'mtllib':
                    if current_object:
                        current_object.parse_mtllib(data)
                    else:
                        self.parse_mtllib(data)
                    continue
                if not current_object and key != 'o':
                    name = os.path.splitext(os.path.basename(file_path))[0]
                    current_object = self.parse_o(name)
                if not current_group and key != 'g':
                    name = os.path.splitext(os.path.basename(file_path))[0]
                    current_group = current_object.parse_g(name)
                if key == 'o':
                    current_object = self.parse_o(data)
                    continue
                if key == 'g':
                    current_group = current_object.parse_g(data)
                    continue
                if key == 'v':
                    current_object.parse_v(data)
                    continue
                if key == 'vt':
                    current_object.parse_vt(data)
                    continue
                if key == 'vn':
                    current_object.parse_vn(data)
                    continue
                if key == 'vp':
                    current_object.parse_vp(data)
                    continue
                if key == 'f':
                    current_group.parse_f(data)
                    continue
                if key == 'usemtl':
                    current_group.parse_usemtl(data)
                    continue
                else:
                    sys.stderr.write("[ObjReader] WARNING: Unknown key: {}\n".format(key))
                    continue

    def parse_o(self, line):
        """
        @type line: str
        @rtype: MeshObject
        """
        assert line not in self._objects, "Objects are not unique: {}".format(line)
        self._objects[line] = MeshObject(self._tmp_material_library_file_path)
        return self._objects[line]

    def parse_mtllib(self, line):
        self._tmp_material_library_file_path = line

    def get_facets(self, name=None):
        """

        @rtype: collections.Iterable[((float, float, float), (float, float, float), (float, float, float))]
        """
        if name:
            assert name in self._objects, "Unknown object: {}".format(name)
            for element in self._objects[name].get_facets():
                yield element
        else:
            assert name is None, "Unknown object: {}".format(name)
            for name, mesh_object in self._objects.items():
                for element in mesh_object.get_facets():
                    yield element

    def get_texture_facets(self, name=None):
        """

        @rtype: collections.Iterable[((float, float, float), (float, float, float), (float, float, float))]
        """
        if name:
            assert name in self._objects, "Unknown object: {}".format(name)
            for element in self._objects[name].get_texture_facets():
                yield element
        else:
            assert name is None, "Unknown object: {}".format(name)
            for name, mesh_object in self._objects.items():
                for element in mesh_object.get_texture_facets():
                    yield element

    def get_normals(self, name=None):
        """

        @rtype: collections.Iterable[((float, float, float), (float, float, float), (float, float, float))]
        """
        if name:
            assert name in self._objects, "Unknown object: {}".format(name)
            for element in self._objects[name].get_normals():
                yield element
        else:
            assert name is None, "Unknown object: {}".format(name)
            for name, mesh_object in self._objects.items():
                for element in mesh_object.get_normals():
                    yield element

    def get_names(self):
        """
        @rtype: collections.Iterable[str]
        """
        repr(self._objects.keys())

    def has_triangular_facets(self):
        """
        @rtype: bool
        """
        return all([mesh_object.has_triangular_facets() for name, mesh_object in self._objects.items()])
