from enum import Enum

from conans.errors import ConanException


class PackageType(Enum):
    LIBRARY = "library"  # abstract type, should contain shared option to define
    STATIC = "static-library"
    SHARED = "shared-library"
    HEADER = "header-library"
    BUILD_SCRIPTS = "build-scripts"
    APP = "application"
    PYTHON = "python-require"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.value

    @staticmethod
    def compute_package_type(conanfile):
        # This doesnt implement the header_only option without shared one. Users should define
        # their package_type as they wish in the configure() method

        def deduce_from_options():
            try:
                shared = conanfile.options.shared
            except ConanException:
                pass
            else:
                if shared:
                    return PackageType.SHARED
                else:
                    try:
                        header = conanfile.options.header_only
                    except ConanException:
                        pass
                    else:
                        if header:
                            return PackageType.HEADER
                    return PackageType.STATIC
            return PackageType.UNKNOWN

        conanfile_type = conanfile.package_type
        if conanfile_type is not None:  # Explicit definition in recipe
            try:
                conanfile_type = PackageType(conanfile_type)
            except ValueError:
                raise ConanException(f"{conanfile}: Invalid package type '{conanfile_type}'. "
                                     f"Valid types: {[i.value for i in PackageType]}")
            if conanfile_type is PackageType.LIBRARY:
                conanfile_type = deduce_from_options()
                if conanfile_type is PackageType.UNKNOWN:
                    raise ConanException("Package type is 'library',"
                                         " but no 'shared' option declared")
            conanfile.package_type = conanfile_type
        else:  # automatic default detection with option shared/header-only
            conanfile.package_type = deduce_from_options()