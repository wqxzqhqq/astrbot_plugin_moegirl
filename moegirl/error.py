"""异常分类"""

from __future__ import annotations



class MoegirlError(Exception):
	"""萌娘百科异常基类"""
	pass
     
class MoegirlUpstreamError(MoegirlError):
	pass

class MoegirlAclError(MoegirlUpstreamError):
	pass

class MoegirlRateLimitedError(MoegirlUpstreamError):
	pass

class MoegirlTimeoutError(MoegirlUpstreamError):
	pass

class MoegirlPageMissingError(MoegirlError):
	pass

class MoegirlDisambiguationError(MoegirlError):
	pass
