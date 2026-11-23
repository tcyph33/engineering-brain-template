"""GitHub: answers questions about pointers' target files, through the signed-in gh CLI."""

from __future__ import annotations

import base64
import binascii
import json
import re
import shutil
import subprocess
import urllib.parse
from types import MappingProxyType
from typing import Mapping, Optional, cast


class GitHubLookupError(Exception):
    """Raised when GitHub can't answer a question about a pointer's target."""


# Proof that a GitHub connection came from GitHub.connect(), which checks gh first.
_CONNECTION_KEY: object = object()


class GitHub:
    """GitHub, reached through the signed-in gh CLI. Get one with GitHub.connect()."""

    def __init__(self, gh_executable: str, connection_key: object) -> None:
        """Creates a connection; only GitHub.connect() can, since only it has the key.

        Args:
            gh_executable: The path to gh, as GitHub.connect() found it.
            connection_key: The module's private key, proving gh was checked first.

        Raises:
            TypeError: If called with any other key, that is, not through connect().
        """
        # Refuse to be built without connect()'s check
        is_from_connect: bool = (connection_key is _CONNECTION_KEY)
        if not is_from_connect:
            raise TypeError("get a GitHub connection with GitHub.connect()")

        # Keep the checked gh path and a per-scan cache of default branches
        self._gh_executable: str = gh_executable
        self._default_branches: dict[str, str] = {}

    @classmethod
    def connect(cls) -> Optional[GitHub]:
        """Connects to GitHub when the gh CLI is installed and signed in.

        Returns:
            The connection, or None when gh can't be used.
        """
        # Find gh
        GH_COMMAND: str = "gh"
        found_executable: Optional[str] = shutil.which(GH_COMMAND)
        is_installed: bool = (found_executable is not None)
        if not is_installed:
            return None
        gh_executable: str = cast(str, found_executable)

        # Check it's signed in
        authentication_status: subprocess.CompletedProcess[str] = subprocess.run(
            [gh_executable, "auth", "status"], capture_output=True, text=True
        )
        is_signed_in: bool = (authentication_status.returncode == 0)
        if not is_signed_in:
            return None
        connection: GitHub = cls(gh_executable, _CONNECTION_KEY)
        return connection

    def file_text(self, repository: str, path: str) -> Optional[str]:
        """Fetches a file's text from a repository's default branch.

        Args:
            repository: The repository, as "owner/name".
            path: The file's path in the repository.

        Returns:
            The file's text, or None when the file doesn't exist.

        Raises:
            GitHubLookupError: If GitHub can't be asked, answers unexpectedly, or the file is
                too large for its contents API (over 1 MB).
        """
        # Ask for the file; a missing file is an answer, not a failure
        response: Optional[object] = self._call_api(
            f"repos/{_encode_url_path(repository)}/contents/{_encode_url_path(path)}"
        )
        is_found: bool = (response is not None)
        if not is_found:
            return None

        # A folder comes back as a list of its files
        is_folder: bool = (isinstance(response, list))
        if is_folder:
            raise GitHubLookupError("the path is a folder; point at a file")

        # Refuse files GitHub won't send inline; it marks them with an encoding other than base64
        ENCODING_KEY: str = "encoding"
        BASE64_ENCODING: str = "base64"
        file_details: Mapping[str, object] = _require_mapping(response)
        encoding: str = _require_text(file_details.get(ENCODING_KEY), ENCODING_KEY)
        is_inline_content: bool = (encoding == BASE64_ENCODING)
        if not is_inline_content:
            raise GitHubLookupError("the file is too large for GitHub to send its content")

        # Decode the content; undecodable bytes can't match a symbol name, so replace them
        CONTENT_KEY: str = "content"
        content: str = _require_text(file_details.get(CONTENT_KEY), CONTENT_KEY)
        try:
            file_bytes: bytes = base64.b64decode(content)
        except binascii.Error as error:
            raise GitHubLookupError(f"GitHub sent content that isn't base64: {error}") from error
        file_text: str = file_bytes.decode("utf-8", errors="replace")
        return file_text

    def has_file_changed_since_commit(self, repository: str, path: str, commit: str) -> bool:
        """Whether a file changed on the default branch after a commit.

        GitHub's comparison lists at most 300 changed files, so a change in a very large
        comparison can be missed.

        Args:
            repository: The repository, as "owner/name".
            path: The file's path in the repository.
            commit: The commit the file was last verified at.

        Returns:
            True when the file changed after that commit.

        Raises:
            GitHubLookupError: If GitHub can't be asked, answers unexpectedly, or doesn't
                know the commit.
        """
        # Compare the verified commit with the default branch
        COMPARISON_SEPARATOR: str = "..."
        branch: str = self._default_branch(repository)
        comparison_range: str = (
            f"{_encode_url_path(commit)}{COMPARISON_SEPARATOR}{_encode_url_path(branch)}"
        )
        comparison: Optional[object] = self._call_api(
            f"repos/{_encode_url_path(repository)}/compare/{comparison_range}"
        )
        is_known_commit: bool = (comparison is not None)
        if not is_known_commit:
            raise GitHubLookupError(f"commit {commit} isn't in {repository}")

        # Look for the file among the changed files
        FILES_KEY: str = "files"
        changed_files: tuple[object, ...] = _require_list(
            _require_mapping(comparison).get(FILES_KEY, []), FILES_KEY
        )
        changed_file: object
        for changed_file in changed_files:
            FILENAME_KEY: str = "filename"
            changed_path: str = _require_text(
                _require_mapping(changed_file).get(FILENAME_KEY), FILENAME_KEY
            )
            is_pointed_file: bool = (changed_path == path)
            if is_pointed_file:
                return True
        return False

    def has_file_changed_since_date(self, repository: str, path: str, date: str) -> bool:
        """Whether a file changed on the default branch after a day.

        A verified date has no time, so only commits after the end of that day count: a
        change made the same day is taken to be the one that was verified.

        Args:
            repository: The repository, as "owner/name".
            path: The file's path in the repository.
            date: The day the file was last verified, as YYYY-MM-DD.

        Returns:
            True when a commit after that day changed the file.

        Raises:
            GitHubLookupError: If GitHub can't be asked or answers unexpectedly.
        """
        # Ask for commits to the file after that day
        END_OF_DAY_UTC: str = "T23:59:59Z"
        branch: str = self._default_branch(repository)
        BRANCH_PARAMETER: str = "sha"
        PATH_PARAMETER: str = "path"
        SINCE_PARAMETER: str = "since"
        query: str = urllib.parse.urlencode({
            BRANCH_PARAMETER: branch,
            PATH_PARAMETER: path,
            SINCE_PARAMETER: f"{date}{END_OF_DAY_UTC}",
        })
        commits: tuple[object, ...] = _require_list(
            self._call_api(f"repos/{_encode_url_path(repository)}/commits?{query}"), "commits"
        )
        has_changed: bool = (len(commits) > 0)
        return has_changed

    def _default_branch(self, repository: str) -> str:
        """Looks up a repository's default branch, once per repository per scan.

        Args:
            repository: The repository, as "owner/name".

        Returns:
            The default branch's name.

        Raises:
            GitHubLookupError: If the repository can't be read.
        """
        # Use the branch already looked up for this repository
        is_cached: bool = (repository in self._default_branches)
        if is_cached:
            cached_branch: str = self._default_branches[repository]
            return cached_branch

        # Otherwise ask GitHub, and remember the answer
        DEFAULT_BRANCH_KEY: str = "default_branch"
        repository_details: Optional[object] = self._call_api(
            f"repos/{_encode_url_path(repository)}"
        )
        is_readable_repository: bool = (repository_details is not None)
        if not is_readable_repository:
            raise GitHubLookupError(f"{repository} doesn't exist or can't be read")
        branch: str = _require_text(
            _require_mapping(repository_details).get(DEFAULT_BRANCH_KEY), DEFAULT_BRANCH_KEY
        )
        self._default_branches[repository] = branch
        return branch

    def _call_api(self, endpoint: str) -> Optional[object]:
        """Calls the GitHub API through gh.

        Args:
            endpoint: The API path, with every part already URL-encoded.

        Returns:
            The parsed JSON response, or None when GitHub answers 404 Not Found.

        Raises:
            GitHubLookupError: If the call fails for any other reason, or the response
                isn't JSON.
        """
        # Call the API
        response: subprocess.CompletedProcess[str] = subprocess.run(
            [self._gh_executable, "api", endpoint], capture_output=True, text=True
        )
        is_failure: bool = (response.returncode != 0)

        # Treat a 404 as "not found"; gh has no exit code for it, only "(HTTP 404)" on stderr
        HTTP_NOT_FOUND_PATTERN: re.Pattern[str] = re.compile(r"\(HTTP 404\)")
        not_found_match: Optional[re.Match[str]] = HTTP_NOT_FOUND_PATTERN.search(response.stderr)
        has_not_found_marker: bool = (not_found_match is not None)
        is_http_404: bool = (is_failure and has_not_found_marker)
        if is_http_404:
            return None

        # Treat any other failure as a failed lookup
        if is_failure:
            raise GitHubLookupError(response.stderr.strip())

        # Parse the answer
        try:
            parsed_response: object = json.loads(response.stdout)
        except json.JSONDecodeError as error:
            raise GitHubLookupError(f"GitHub's answer wasn't JSON: {error}") from error
        return parsed_response


def _encode_url_path(path_part: str) -> str:
    """URL-encodes part of a GitHub API path, keeping its slashes.

    Args:
        path_part: A repository, file path, commit, or branch.

    Returns:
        The encoded part.
    """
    # Keep slashes, which separate the path's own segments
    encoded_part: str = urllib.parse.quote(path_part, safe="/")
    return encoded_part


def _require_mapping(value: object) -> Mapping[str, object]:
    """Checks a GitHub answer is a JSON object.

    Args:
        value: Part of a parsed GitHub response.

    Returns:
        A read-only view of the object.

    Raises:
        GitHubLookupError: If it isn't a JSON object.
    """
    # Reject anything but an object
    is_mapping: bool = (isinstance(value, dict))
    if not is_mapping:
        raise GitHubLookupError("GitHub's answer had an unexpected shape")
    mapping: Mapping[str, object] = MappingProxyType(cast(dict, value))
    return mapping


def _require_list(value: object, field_name: str) -> tuple[object, ...]:
    """Checks part of a GitHub answer is a JSON list.

    Args:
        value: Part of a parsed GitHub response.
        field_name: The field it came from, for the error message.

    Returns:
        The list's items, as a tuple.

    Raises:
        GitHubLookupError: If it isn't a JSON list.
    """
    # Reject anything but a list
    is_list: bool = (isinstance(value, list))
    if not is_list:
        raise GitHubLookupError(f"GitHub's answer had no list of {field_name}")
    items: tuple[object, ...] = tuple(cast(list, value))
    return items


def _require_text(value: object, field_name: str) -> str:
    """Checks part of a GitHub answer is a JSON string.

    Args:
        value: Part of a parsed GitHub response.
        field_name: The field it came from, for the error message.

    Returns:
        The string.

    Raises:
        GitHubLookupError: If it isn't a JSON string.
    """
    # Reject anything but a string
    is_text: bool = (isinstance(value, str))
    if not is_text:
        raise GitHubLookupError(f"GitHub's answer had no {field_name}")
    text: str = cast(str, value)
    return text
