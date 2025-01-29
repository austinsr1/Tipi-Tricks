import pytest
from click.testing import CliRunner
from unittest.mock import patch, mock_open

import tipi_tricks  # Your script renamed to tipi_tricks.py

@pytest.fixture
def runner():
    return CliRunner()


#
# 1. General Commands
#

def test_tipi_tricks_help(runner):
    """Test that the main script shows help."""
    result = runner.invoke(tipi_tricks.tipi_tricks, ["--help"])
    assert result.exit_code == 0
    assert "Tipi tricks command group." in result.output

def test_clear_cache(runner):
    """Test the 'clear-cache' command (note the dash)."""
    with patch("subprocess.run") as mock_subprocess:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["clear-cache"])
        assert result.exit_code == 0
        assert "Clearing Docker cache..." in result.output
        assert "Docker cache cleared successfully." in result.output
        mock_subprocess.assert_called_with(["docker", "system", "prune", "-a", "-f"], check=True)


#
# 2. Updates: Tipi, App, System
#

def test_updates_tipi_enable(runner):
    """Test 'updates tipi enable' command."""
    fake_crontab_content = ""
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["updates", "tipi", "enable"])
        assert result.exit_code == 0
        assert "Enabling Tipi Auto Updates." in result.output
        mocked_file.assert_called_with(tipi_tricks.CRONTAB_FILE, "a")

def test_updates_tipi_disable(runner):
    """Test 'updates tipi disable' command."""
    fake_crontab_content = tipi_tricks.TIPI_CRON_ENTRY
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["updates", "tipi", "disable"])
        assert result.exit_code == 0
        assert "Disabling Tipi Auto Updates." in result.output
        calls = [call_args[0][0] for call_args in mocked_file.call_args_list]
        assert calls.count(tipi_tricks.CRONTAB_FILE) == 2

def test_updates_app_enable(runner):
    """Test 'updates app enable' command."""
    fake_crontab_content = ""
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["updates", "app", "enable"])
        assert result.exit_code == 0
        assert "Enabling App Auto Updates." in result.output
        mocked_file.assert_called_with(tipi_tricks.CRONTAB_FILE, "a")

def test_updates_app_disable(runner):
    """Test 'updates app disable' command."""
    fake_crontab_content = tipi_tricks.APP_CRON_ENTRY
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["updates", "app", "disable"])
        assert result.exit_code == 0
        assert "Disabling App Auto Updates." in result.output

def test_updates_system_enable(runner):
    """Test 'updates system enable' command."""
    fake_crontab_content = ""
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["updates", "system", "enable"])
        assert result.exit_code == 0
        assert "Enabling System Auto Updates." in result.output
        mocked_file.assert_called_with(tipi_tricks.CRONTAB_FILE, "a")

def test_updates_system_disable(runner):
    """Test 'updates system disable' command."""
    fake_crontab_content = tipi_tricks.SYSTEM_CRON_ENTRY
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["updates", "system", "disable"])
        assert result.exit_code == 0
        assert "Disabling System Auto Updates." in result.output


#
# 3. Backup commands
#

def test_backup_tipi_enable(runner):
    """Test 'backup tipi-backup enable' command (note the dash)."""
    fake_crontab_content = ""
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["backup", "tipi-backup", "enable"])
        assert result.exit_code == 0
        assert "Enabling Tipi Backup." in result.output
        mocked_file.assert_called_with(tipi_tricks.CRONTAB_FILE, "a")

def test_backup_tipi_disable(runner):
    """Test 'backup tipi-backup disable' command (note the dash)."""
    fake_crontab_content = tipi_tricks.BACKUP_CRON_ENTRY
    with patch("builtins.open", mock_open(read_data=fake_crontab_content)) as mocked_file:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["backup", "tipi-backup", "disable"])
        assert result.exit_code == 0
        assert "Disabling Tipi Backup." in result.output


#
# 4. Monitors: mount-points, drive-space, temp-sensor
#

def test_monitors_mount_points_enable(runner):
    """Test 'monitors mount-points enable' command (note the dash)."""
    with patch("tipi_tricks.create_service_file") as mock_service_file, \
         patch("tipi_tricks.enable_service") as mock_enable_service:
        
        result = runner.invoke(tipi_tricks.tipi_tricks, ["monitors", "mount-points", "enable"])
        assert result.exit_code == 0
        assert "Enabling mount points monitoring..." in result.output
        mock_service_file.assert_called_once()
        mock_enable_service.assert_called_once()

def test_monitors_mount_points_disable(runner):
    """Test 'monitors mount-points disable' command (note the dash)."""
    with patch("tipi_tricks.disable_service") as mock_disable_service, \
         patch("tipi_tricks.remove_service_file") as mock_remove_service:
        
        result = runner.invoke(tipi_tricks.tipi_tricks, ["monitors", "mount-points", "disable"])
        assert result.exit_code == 0
        assert "Disabling mount points monitoring..." in result.output
        mock_disable_service.assert_called_once()
        mock_remove_service.assert_called_once()

def test_monitors_drive_space_enable(runner):
    """Test 'monitors drive-space enable' command (note the dash)."""
    with patch("tipi_tricks.create_service_file") as mock_service_file, \
         patch("tipi_tricks.enable_service") as mock_enable_service:
        
        result = runner.invoke(tipi_tricks.tipi_tricks, ["monitors", "drive-space", "enable"])
        assert result.exit_code == 0
        assert "Enabling drive space monitoring..." in result.output
        mock_service_file.assert_called_once()
        mock_enable_service.assert_called_once()

def test_monitors_drive_space_disable(runner):
    """Test 'monitors drive-space disable' command (note the dash)."""
    with patch("tipi_tricks.disable_service") as mock_disable_service, \
         patch("tipi_tricks.remove_service_file") as mock_remove_service:
        
        result = runner.invoke(tipi_tricks.tipi_tricks, ["monitors", "drive-space", "disable"])
        assert result.exit_code == 0
        assert "Disabling drive space monitoring..." in result.output
        mock_disable_service.assert_called_once()
        mock_remove_service.assert_called_once()

def test_monitors_temp_sensor_install(runner):
    """Test 'monitors temp-sensor install' command (note the dash)."""
    with patch("subprocess.run") as mock_subprocess:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["monitors", "temp-sensor", "install"])
        assert result.exit_code == 0
        assert "Installing temp sensor monitoring..." in result.output
        assert mock_subprocess.call_count == 2

def test_monitors_temp_sensor_uninstall(runner):
    """Test 'monitors temp-sensor uninstall' command (note the dash)."""
    with patch("subprocess.run") as mock_subprocess:
        result = runner.invoke(tipi_tricks.tipi_tricks, ["monitors", "temp-sensor", "uninstall"])
        assert result.exit_code == 0
        assert "Uninstalling temp sensor monitoring..." in result.output
        mock_subprocess.assert_called_once()
