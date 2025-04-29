import subprocess
from pathlib import Path  # Use pathlib for better path handling
from typing import Literal

from ..config.settings import settings

PACKAGE_PATH = (
    settings.base_dir / "vendor" / "DiffRhythm"
)  # Adjusted to use settings.base_dir
if not PACKAGE_PATH.exists():
    raise FileNotFoundError(f"DiffRhythm package not found at {PACKAGE_PATH}")


class DiffRhythm:
    def __init__(self, package_path: Path | None = None):  # Use Path | None
        """
        Initializes the DiffRhythm wrapper.

        Args:
            package_path: Optional path to the root directory of the DiffRhythm code.
                          If None, defaults to PACKAGE_PATH defined above.
        """
        self.data_dir = settings.data_dir
        # Use default from global scope if None
        resolved_package_path = (
            Path(package_path).resolve() if package_path else PACKAGE_PATH
        )

        if not resolved_package_path.is_dir():
            # Check the default if package_path was None and failed, or raise if specified path failed
            if package_path is None and not PACKAGE_PATH.is_dir():
                raise FileNotFoundError(
                    f"DiffRhythm package root not found at default location: {PACKAGE_PATH}"
                )
            elif package_path is not None:
                raise FileNotFoundError(
                    f"DiffRhythm package root not found at specified path: {resolved_package_path}"
                )
            else:  # Should technically be covered, but for safety
                self.package_path = PACKAGE_PATH  # Fallback just in case
        else:
            self.package_path = resolved_package_path

        print(f"DiffRhythm package path set to: {self.package_path}")

        # Determine absolute path to the shell script
        # *** Adjust the relative path if your script is located differently ***
        self.shell_script_path = (
            # settings.base_dir / "scripts" / "music_generation" / "run_diffrhythm.sh"
            self.package_path / "scripts" / "run_diffrhythm.sh"
        ).resolve()
        if not self.shell_script_path.is_file():
            raise FileNotFoundError(
                f"DiffRhythm shell script not found at {self.shell_script_path}"
            )
        print(f"Using DiffRhythm shell script: {self.shell_script_path.relative_to(settings.base_dir)}")

    def _call_diffrhythm_bash_script(
        self,
        lrc_path: str | Path | None = None,  # Use | None
        ref_prompt: str | None = None,  # Use | None
        ref_audio_path: str | Path | None = None,  # Use | None
        chunked: bool = False,
        audio_length: Literal[95, 285] = 285,
        repo_id: str = "ASLP-lab/DiffRhythm-full",
        output_dir: str | Path | None = None,  # Use | None
        output_file_name: str = "output.wav",
    ) -> bool:
        """
        Calls the DiffRhythm bash script using named arguments via subprocess.

        Args:
            lrc_path: Optional path to the lyrics file (--lrc-path).
            ref_prompt: Optional reference text prompt (--ref-prompt).
            ref_audio_path: Optional path to reference audio (--ref-audio-path).
            chunked: If True, pass --chunked flag.
            audio_length: Pass --audio-length {95|285}.
            repo_id: Pass --repo-id REPO_ID.
            output_dir: Optional path to output directory (--output-dir). If None, script uses its default.

        Returns:
            True if the script executed successfully (exit code 0), False otherwise.
        """
        try:
            # --- Prepare Command and Arguments for the Bash Script ---
            cmd = ["/bin/bash", str(self.shell_script_path)]

            if lrc_path:
                cmd.extend(["--lrc-path", str(Path(lrc_path).resolve())])
            if ref_prompt:
                cmd.extend(["--ref-prompt", ref_prompt])
            if ref_audio_path:
                cmd.extend(["--ref-audio-path", str(Path(ref_audio_path).resolve())])
            if chunked:
                cmd.append("--chunked")
            cmd.extend(["--audio-length", str(audio_length)])
            cmd.extend(["--repo-id", repo_id])
            if output_dir:
                cmd.extend(["--output-dir", str(Path(output_dir).resolve())])
            cmd.extend(["--output-file-name", output_file_name])

            print(f"Executing shell script: {' '.join(cmd)}")

            # --- Execute ---
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            print("\n--- Shell Script Execution Successful ---")
            print("stdout:\n", result.stdout)
            if result.stderr:
                print("stderr:\n", result.stderr)
            return True

        except FileNotFoundError as e:
            print(
                f"\nError: File not found during execution (/bin/bash or script): {e}"
            )
            return False
        except subprocess.CalledProcessError as e:
            print(
                f"\nError: Shell script execution failed (return code {e.returncode})"
            )
            print("stdout:\n", e.stdout)
            print("stderr:\n", e.stderr)
            return False
        except Exception as e:
            print(f"\nAn unexpected Python error occurred: {e}")
            return False

    def generate_music(
        self,
        prompt: str | None = None,
        lrc_path: str | Path | None = None,
        audio_length: Literal[95, 285] = 95,
        ref_audio_path: str | Path | None = None,
        instrumental_only: bool = False,
        output_dir: str | Path | None = None,
        output_file_name: str = "output.wav",
        chunked: bool = True,
        repo_id: str = "ASLP-lab/DiffRhythm-full",
    ) -> Path | None:
        """
        Generates music by calling the DiffRhythm shell script with named arguments.

        Args:
             prompt: The reference text prompt (--ref-prompt). Uses script default if None.
             lrc_path: Optional path to lyrics file (--lrc-path). Uses script default if None.
             audio_length: Audio length, 95 or 285 (--audio-length).
             ref_audio_path: Optional path to reference audio file (--ref-audio-path).
             instrumental_only: If True and lrc_path not given, ensures --lrc-path is omitted.
             output_dir: Directory to save output. If None, script uses its internal default.
             chunked: Whether to use chunked decoding (--chunked).
             repo_id: Model repository ID (--repo-id).

        Returns:
            The absolute path to the generated music file if successful, otherwise None.
        """
        if lrc_path:
            actual_lrc_path = Path(lrc_path)
        else:
            actual_lrc_path = (
                self.data_dir / "music_generation" / "lrc" / "eg_en_full.lrc"
            )
            print(f"LRC path not provided, using script default: {actual_lrc_path}")
            # If no lrc_path is provided and instrumental_only is True, use the default empty LRC
            if instrumental_only:
                actual_lrc_path = (
                    self.data_dir / "music_generation" / "music" / "empty.lrc"
                )
                print(
                    "Instrumental only specified, using script's default LRC handling."
                )

        if prompt and ref_audio_path:
            print("Both prompt and reference audio path provided, using prompt only.")
            ref_audio_path = None  # Ignore ref_audio_path if prompt is given

        if output_dir:
            effective_output_dir = Path(output_dir).resolve()
            try:
                effective_output_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(
                    f"Warning: Could not create specified output directory {effective_output_dir}: {e}"
                )
        else:
            effective_output_dir = (
                self.package_path / "infer" / "example" / "output"
            ).resolve()
            print(
                f"Output directory not specified, expecting output in script default: {effective_output_dir}"
            )

        if audio_length not in [95, 285]:
            raise ValueError("audio_length must be either 95 or 285 seconds.")

        expected_output_file = effective_output_dir / output_file_name

        success = self._call_diffrhythm_bash_script(
            lrc_path=actual_lrc_path,
            ref_prompt=prompt,
            ref_audio_path=ref_audio_path,
            chunked=chunked,
            audio_length=audio_length,
            repo_id=repo_id,
            output_dir=output_dir,  # Pass None or the specified dir
            output_file_name=output_file_name,
        )

        if success:
            if expected_output_file.is_file():
                print(f"Successfully generated: {expected_output_file}")
                return expected_output_file
            else:
                print(
                    f"Error: Script reported success, but output file not found at {expected_output_file}"
                )
                # Attempt to find output.wav in the hardcoded relative path just in case CWD was different
                # This alt check might be less relevant now output_dir is handled better
                alt_expected_output = (
                    self.package_path / "infer" / "example" / "output" / "output.wav"
                )
                if alt_expected_output.is_file():
                    print(
                        f"Found output at alternative path: {alt_expected_output.resolve()}"
                    )
                    return alt_expected_output.resolve()
                return None
        else:
            print("Music generation via shell script failed.")
            return None


# class DiffRhythm:
#     def __init__(self, package_path: Path | None = PACKAGE_PATH):
#         if package_path is None:
#             package_path = (
#                 settings.base_dir / "vendor" / "DiffRhythm"
#             ).resolve()  # Adjusted to use settings.base_dir
#         if not package_path.exists():
#             raise FileNotFoundError(f"DiffRhythm package not found at {package_path}")
#         self.package_path = package_path

#     def _run_diff_rhythm_inference(
#         self,
#         lrc_path: Optional[str | Path] = None,
#         ref_prompt: Optional[str] = None,
#         ref_audio_path: Optional[str | Path] = None,
#         chunked: bool = False,
#         audio_length: Literal[95, 285] = 95,
#         repo_id: str = "ASLP-lab/DiffRhythm-base",
#         output_dir: str | Path = "infer/example/output",
#         script_path: str | Path | None = None,
#         cuda_device: int | None = 0,
#     ) -> bool:
#         """
#         Runs the inference script as a subprocess.

#         Args:
#             script_path: Path to the inference_script.py file.
#             lrc_path: Path to the lyrics file.
#             ref_prompt: Reference text prompt for style.
#             ref_audio_path: Path to the reference audio file for style.
#             chunked: Whether to use chunked decoding.
#             audio_length: Length of the generated audio (95 or 285 seconds).
#             repo_id: Hugging Face repository ID for the model.
#             output_dir: Directory to save the generated output WAV file.

#         Returns:
#             True if the script executed successfully, False otherwise.
#         """
#         if not script_path:
#             script_path = self.package_path / "infer" / "infer.py"
#         script_path = Path(script_path).resolve()  # Ensure absolute path
#         script_dir = script_path.parent  # Get the directory containing the script

#         if not script_path.is_file():
#             print(f"Error: Script not found at {script_path}")
#             return False

#         sub_env = copy.deepcopy(os.environ)

#         if cuda_device is not None and torch.cuda.is_available():
#             sub_env["CUDA_VISIBLE_DEVICES"] = str(cuda_device)
#             print(
#                 f"Subprocess CUDA_VISIBLE_DEVICES set to: {sub_env.get('CUDA_VISIBLE_DEVICES')}"
#             )

#         root_path_str = str(self.package_path)
#         existing_pp = sub_env.get("PYTHONPATH", "")
#         separator = os.pathsep
#         if existing_pp:
#             sub_env["PYTHONPATH"] = f"{root_path_str}{separator}{existing_pp}"
#         else:
#             sub_env["PYTHONPATH"] = root_path_str

#         print(f"Subprocess PYTHONPATH set to: {sub_env.get('PYTHONPATH')}")

#         # Use the same Python interpreter that's running this wrapper function
#         python_executable = sys.executable
#         print(f"Using Python executable: {python_executable}")

#         # Build the command list
#         cmd = [python_executable, str(script_path)]

#         if lrc_path:
#             cmd.extend(["--lrc-path", str(Path(lrc_path).resolve())])
#         if ref_prompt:
#             cmd.extend(["--ref-prompt", ref_prompt])
#         if ref_audio_path:
#             cmd.extend(["--ref-audio-path", str(Path(ref_audio_path).resolve())])
#         if chunked:
#             cmd.append("--chunked")  # Action flag, no value needed

#         # Add arguments with default values too, so the script receives them explicitly
#         cmd.extend(["--audio-length", str(audio_length)])
#         cmd.extend(["--repo_id", repo_id])
#         cmd.extend(
#             ["--output-dir", str(Path(output_dir).resolve())]
#         )  # Resolve output dir relative to current location or make absolute

#         print(f"Running command: {' '.join(cmd)}")
#         print(f"Working directory: {script_dir}")

#         try:
#             # Run the subprocess
#             # Set cwd to the script's directory in case it uses relative paths for imports or assets
#             result = subprocess.run(
#                 cmd,
#                 check=True,  # Raise CalledProcessError if return code is non-zero
#                 capture_output=True,  # Capture stdout and stderr
#                 text=True,  # Decode output as text
#                 encoding="utf-8",  # Specify encoding
#                 cwd=script_dir,  # Set the working directory
#             )
#             print("Script executed successfully.")
#             print("stdout:\n", result.stdout)
#             if result.stderr:
#                 print(
#                     "stderr:\n", result.stderr
#                 )  # Print stderr even on success if it exists
#             return True

#         except FileNotFoundError:
#             print(
#                 f"Error: Python executable not found at {python_executable} or script missing."
#             )
#             return False
#         except subprocess.CalledProcessError as e:
#             print(f"Error: Script execution failed with return code {e.returncode}")
#             print("stdout:\n", e.stdout)
#             print("stderr:\n", e.stderr)
#             return False
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
#             return False

#     def generate_music(
#         self,
#         prompt: str,
#         lrc_path: str | Path = "",
#         audio_length: Literal[95, 285] = 285,
#         ref_audio_path: str | Path = "",
#         instrumental_only: bool = False,
#         output_dir: str | Path = ".",
#     ) -> Path | None:
#         """
#         Generates music based on the provided prompt. Returns the path to the generated music file.
#         """
#         if not lrc_path:
#             if instrumental_only:
#                 lrc_path = (
#                     settings.data_dir / "music_generation" / "empty.lrc"
#                 ).resolve()
#             else:
#                 raise ValueError("LRC path must be provided for music generation.")
#         diff_rhythm = DiffRhythm()
#         success = diff_rhythm._run_diff_rhythm_inference(
#             lrc_path=lrc_path,
#             ref_prompt=prompt,
#             ref_audio_path=ref_audio_path,
#             chunked=True,
#             audio_length=audio_length,
#             repo_id="ASLP-lab/DiffRhythm-base",
#             output_dir=output_dir,
#         )
#         if success:
#             return (
#                 Path(output_dir) / "output.wav"
#             ).resolve()  # output.wav is hardcoded in the script
#         else:
#             return None


if __name__ == "__main__":
    model = DiffRhythm()
    # Example usage
    prompt = "Lo-fi music with the flute"
    model.generate_music(
        prompt=prompt,
        instrumental_only=True,
    )
