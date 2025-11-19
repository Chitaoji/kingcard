"""
# kingcard
A template repository for building python packages. Please replace `$package` with the
package's name in `metadata.yml`.

## See Also
### Github repository
* https://github.com/Chitaoji/kingcard/

### PyPI project
* https://pypi.org/project/kingcard/

## License
This project falls under the BSD 3-Clause License.

"""

from . import core
from .__version__ import __version__
from .core import *

__all__: list[str] = []
__all__.extend(core.__all__)
