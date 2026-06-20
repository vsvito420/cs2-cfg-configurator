Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml

$script:AppName = 'CS2 Config Manager'
$script:KnownCommands = @(
    [pscustomobject]@{ Name='rate'; Category='Netzwerk'; Description='Maximale akzeptierte Spielbandbreite'; DefaultValue='786432' },
    [pscustomobject]@{ Name='fps_max'; Category='Performance'; Description='FPS-Limit im Match'; DefaultValue='0' },
    [pscustomobject]@{ Name='fps_max_ui'; Category='Performance'; Description='FPS-Limit im Menü'; DefaultValue='120' },
    [pscustomobject]@{ Name='snd_mute_losefocus'; Category='Audio'; Description='Mute bei Alt-Tab'; DefaultValue='0' },
    [pscustomobject]@{ Name='cl_crosshair_friendly_warning'; Category='HUD'; Description='Freund-Warnung im Crosshair'; DefaultValue='0' },
    [pscustomobject]@{ Name='bind'; Category='Bind'; Description='Tastenbelegung'; DefaultValue='bind mouse5 slot12' },
    [pscustomobject]@{ Name='viewmodel_fov'; Category='Viewmodel'; Description='Viewmodel FOV'; DefaultValue='68' },
    [pscustomobject]@{ Name='sensitivity'; Category='Maus'; Description='Maus-Sensitivität'; DefaultValue='1.0' }
)

function Get-DefaultConfigDir {
    $candidates = @(
        'G:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg',
        'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg',
        'D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg'
    )
    foreach ($candidate in $candidates) { if (Test-Path $candidate) { return $candidate } }
    return $candidates[0]
}

function Get-CfgFiles {
    if (-not (Test-Path $script:ConfigDir)) { return @() }
    Get-ChildItem -Path $script:ConfigDir -Filter '*.cfg' -File | Sort-Object Name
}

function Get-CommandObjectsFromText([string]$text) {
    $rows = New-Object 'System.Collections.ObjectModel.ObservableCollection[object]'
    $lineNumber = 0
    foreach ($line in ($text -split "`r?`n")) {
        $lineNumber++
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) {
            $rows.Add([pscustomobject]@{ Line=$lineNumber; Enabled=$true; Command=''; Value=''; Note='Leerzeile' })
            continue
        }
        if ($trimmed.StartsWith('//')) {
            $rows.Add([pscustomobject]@{ Line=$lineNumber; Enabled=$false; Command='//'; Value=$trimmed.Substring(2).Trim(); Note='Kommentar' })
            continue
        }
        $parts = $trimmed.Split(@(' '), 2, [System.StringSplitOptions]::RemoveEmptyEntries)
        $cmd = $parts[0]
        $val = if ($parts.Count -gt 1) { $parts[1] } else { '' }
        $rows.Add([pscustomobject]@{ Line=$lineNumber; Enabled=$true; Command=$cmd; Value=$val; Note='' })
    }
    return $rows
}

function Convert-CommandObjectsToText($items) {
    (($items | ForEach-Object {
        if ($_.Command -eq '//') { '// ' + $_.Value }
        elseif ([string]::IsNullOrWhiteSpace($_.Command) -and [string]::IsNullOrWhiteSpace($_.Value)) { '' }
        elseif (-not $_.Enabled) { '// ' + $_.Command + ' ' + $_.Value }
        elseif ([string]::IsNullOrWhiteSpace($_.Value)) { $_.Command }
        else { ($_.Command.Trim() + ' ' + $_.Value.Trim()).Trim() }
    }) -join [Environment]::NewLine)
}

$script:ConfigDir = Get-DefaultConfigDir
$script:CurrentFile = $null

[xml]$xaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="CS2 Config Manager" Height="720" Width="1160" WindowStartupLocation="CenterScreen">
  <Grid Margin="12">
    <Grid.RowDefinitions>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="*"/>
      <RowDefinition Height="Auto"/>
    </Grid.RowDefinitions>
    <StackPanel Grid.Row="0" Orientation="Horizontal" Margin="0,0,0,8">
      <Button x:Name="btnDetect" Content="Detect Path" Margin="0,0,8,0" Padding="10,6"/>
      <Button x:Name="btnBrowse" Content="Ordner wählen" Padding="10,6"/>
    </StackPanel>
    <DockPanel Grid.Row="1" Margin="0,0,0,8">
      <TextBlock Text="CFG-Ordner:" VerticalAlignment="Center" Margin="0,0,8,0"/>
      <TextBox x:Name="txtConfigDir" Height="26"/>
      <Button x:Name="btnSaveDir" Content="Save Path" Margin="8,0,0,0" Padding="10,6"/>
      <Button x:Name="btnOpenFolder" Content="Öffnen" Margin="8,0,0,0" Padding="10,6"/>
    </DockPanel>
    <Grid Grid.Row="2">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="260"/>
        <ColumnDefinition Width="8"/>
        <ColumnDefinition Width="*"/>
      </Grid.ColumnDefinitions>
      <DockPanel Grid.Column="0">
        <StackPanel DockPanel.Dock="Top" Orientation="Horizontal" Margin="0,0,0,8">
          <TextBlock Text="Files" VerticalAlignment="Center" Margin="0,0,10,0" FontWeight="Bold"/>
          <Button x:Name="btnRefresh" Content="Refresh" Margin="0,0,8,0" Padding="10,6"/>
          <Button x:Name="btnNew" Content="New" Padding="10,6"/>
        </StackPanel>
        <ListBox x:Name="listFiles"/>
        <Button x:Name="btnDelete" Content="DEL" DockPanel.Dock="Bottom" Margin="0,8,0,0" Padding="10,6" Background="#FFB00020" Foreground="White" ToolTip="Delete selected file"/>
      </DockPanel>
      <GridSplitter Grid.Column="1" Width="8" HorizontalAlignment="Stretch"/>
      <Grid Grid.Column="2">
        <Grid.RowDefinitions>
          <RowDefinition Height="Auto"/>
          <RowDefinition Height="Auto"/>
          <RowDefinition Height="*"/>
          <RowDefinition Height="Auto"/>
          <RowDefinition Height="220"/>
        </Grid.RowDefinitions>
        <DockPanel Grid.Row="0" Margin="0,0,0,8">
          <TextBlock Text="Active File:" VerticalAlignment="Center" Margin="0,0,8,0"/>
          <TextBlock x:Name="txtCurrentFile" Text="(keine)"/>
          <Button x:Name="btnSave" Content="Save" DockPanel.Dock="Right" Margin="8,0,0,0" Padding="10,6"/>
          <Button x:Name="btnSaveAs" Content="Save As" DockPanel.Dock="Right" Padding="10,6"/>
        </DockPanel>
        <DockPanel Grid.Row="1" Margin="0,0,0,8">
          <TextBlock Text="Commands" VerticalAlignment="Center" Margin="0,0,10,0" FontWeight="Bold"/>
          <ComboBox x:Name="comboCommands" Width="300" DisplayMemberPath="Name"/>
          <Button x:Name="btnAddCommand" Content="Add Row" Margin="8,0,0,0" Padding="10,6" Background="#FF1E88E5" Foreground="White" ToolTip="Add selected command as a new row"/>
        </DockPanel>
        <DataGrid x:Name="gridCommands" Grid.Row="2" AutoGenerateColumns="False" CanUserAddRows="False" CanUserDeleteRows="False" HeadersVisibility="Column" AlternatingRowBackground="#FFF4F7FB" GridLinesVisibility="All">
          <DataGrid.Columns>
            <DataGridTemplateColumn Header="Use" Width="55">
              <DataGridTemplateColumn.CellTemplate>
                <DataTemplate><CheckBox IsChecked="{Binding Enabled}" HorizontalAlignment="Center"/></DataTemplate>
              </DataGridTemplateColumn.CellTemplate>
            </DataGridTemplateColumn>
            <DataGridTextColumn Header="Line" Binding="{Binding Line}" Width="60" IsReadOnly="True"/>
            <DataGridTextColumn Header="Command" Binding="{Binding Command}" Width="180"/>
            <DataGridTextColumn Header="Value" Binding="{Binding Value}" Width="*"/>
            <DataGridTextColumn Header="Hinweis" Binding="{Binding Note}" Width="180" IsReadOnly="True"/>
          </DataGrid.Columns>
        </DataGrid>
        <TextBlock Grid.Row="3" Text="Raw Editor" Margin="0,8,0,4"/>
        <TextBox x:Name="txtEditor" Grid.Row="4" AcceptsReturn="True" AcceptsTab="True" TextWrapping="NoWrap" VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Auto" FontFamily="Consolas" Background="#FF0F172A" Foreground="#FFE2E8F0" CaretBrush="White"/>
      </Grid>
    </Grid>
    <StatusBar Grid.Row="3">
      <StatusBarItem><TextBlock x:Name="txtStatus" Text="Ready"/></StatusBarItem>
    </StatusBar>
  </Grid>
</Window>
'@

$reader = New-Object System.Xml.XmlNodeReader $xaml
$window = [Windows.Markup.XamlReader]::Load($reader)
function Find-Name($n) { $window.FindName($n) }
$btnDetect = Find-Name 'btnDetect'
$btnBrowse = Find-Name 'btnBrowse'
$txtConfigDir = Find-Name 'txtConfigDir'
$btnSaveDir = Find-Name 'btnSaveDir'
$btnOpenFolder = Find-Name 'btnOpenFolder'
$btnRefresh = Find-Name 'btnRefresh'
$btnNew = Find-Name 'btnNew'
$btnDelete = Find-Name 'btnDelete'
$btnSave = Find-Name 'btnSave'
$btnSaveAs = Find-Name 'btnSaveAs'
$comboCommands = Find-Name 'comboCommands'
$btnAddCommand = Find-Name 'btnAddCommand'
$gridCommands = Find-Name 'gridCommands'
$txtEditor = Find-Name 'txtEditor'
$txtCurrentFile = Find-Name 'txtCurrentFile'
$txtStatus = Find-Name 'txtStatus'
$listFiles = Find-Name 'listFiles'

function Refresh-FileList {
    $listFiles.ItemsSource = $null
    $files = Get-CfgFiles
    $listFiles.ItemsSource = $files
    $txtStatus.Text = "CFG-Ordner: $script:ConfigDir | Dateien: $($files.Count)"
}
function Load-File([string]$path) { if (Test-Path $path) { $script:CurrentFile = $path; $txtEditor.Text = Get-Content -Path $path -Raw; $gridCommands.ItemsSource = Get-CommandObjectsFromText $txtEditor.Text; $txtCurrentFile.Text = [IO.Path]::GetFileName($path) } }
function Save-CurrentFile { if (-not $script:CurrentFile) { [System.Windows.MessageBox]::Show('Kein Ziel gewählt. Nutze Neu oder Speichern unter.', $script:AppName) | Out-Null; return }; $txtEditor.Text | Set-Content -Path $script:CurrentFile -Encoding UTF8; $gridCommands.ItemsSource = Get-CommandObjectsFromText $txtEditor.Text; Refresh-FileList }
function Save-AsFile { $dialog = New-Object Microsoft.Win32.SaveFileDialog; $dialog.InitialDirectory = $script:ConfigDir; $dialog.Filter = 'CFG files (*.cfg)|*.cfg'; $dialog.FileName = 'autoexec.cfg'; if ($dialog.ShowDialog()) { $script:CurrentFile = $dialog.FileName; Save-CurrentFile } }
function New-File { $script:CurrentFile = $null; $txtEditor.Text = "// New CS2 Config`nrate 786432`nfps_max 0`nfps_max_ui 120`nsnd_mute_losefocus 0"; $gridCommands.ItemsSource = Get-CommandObjectsFromText $txtEditor.Text; $txtCurrentFile.Text = '(neu)' }
function Delete-SelectedFile {
    if (-not $listFiles.SelectedItem) { return }
    $item = $listFiles.SelectedItem
    $result = [System.Windows.MessageBox]::Show("Delete selected file?`n`n$($item.Name)", $script:AppName, 'YesNo', 'Warning')
    if ($result -ne 'Yes') { return }
    Remove-Item $item.FullName -Force
    if ($script:CurrentFile -eq $item.FullName) { New-File }
    Refresh-FileList
}
function Add-SelectedCommand { $selected = $comboCommands.SelectedItem; if ($selected) { $items = @($gridCommands.ItemsSource); if (-not $items) { $items = @() }; $items += [pscustomobject]@{ Line=($items.Count+1); Enabled=$true; Command=$selected.Name; Value=$selected.DefaultValue; Note=$selected.Description }; $gridCommands.ItemsSource = $items; $txtEditor.Text = Convert-CommandObjectsToText $items } }
function Detect-ConfigDir { $script:ConfigDir = Get-DefaultConfigDir; $txtConfigDir.Text = $script:ConfigDir; Refresh-FileList }

$comboCommands.ItemsSource = $script:KnownCommands
$comboCommands.SelectedIndex = 0
$txtConfigDir.Text = $script:ConfigDir
Refresh-FileList
New-File

$btnDetect.Add_Click({ Detect-ConfigDir })
$btnRefresh.Add_Click({ Refresh-FileList })
$btnNew.Add_Click({ New-File })
$btnSave.Add_Click({ Save-CurrentFile })
$btnSaveAs.Add_Click({ Save-AsFile })
$btnDelete.Add_Click({ Delete-SelectedFile })
$btnAddCommand.Add_Click({ Add-SelectedCommand })
$btnSaveDir.Add_Click({ $script:ConfigDir = $txtConfigDir.Text.Trim(); Refresh-FileList })
$btnBrowse.Add_Click({ Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.SelectedPath = $txtConfigDir.Text; if ($d.ShowDialog() -eq 'OK') { $script:ConfigDir = $d.SelectedPath; $txtConfigDir.Text = $script:ConfigDir; Refresh-FileList } })
$btnOpenFolder.Add_Click({ if (Test-Path $txtConfigDir.Text) { Start-Process explorer.exe $txtConfigDir.Text } })
$listFiles.Add_SelectionChanged({ if ($listFiles.SelectedItem) { Load-File $listFiles.SelectedItem.FullName } })
$gridCommands.Add_CellEditEnding({ $window.Dispatcher.BeginInvoke([action]{ $txtEditor.Text = Convert-CommandObjectsToText @($gridCommands.ItemsSource) }) | Out-Null })
$txtEditor.Add_TextChanged({ $gridCommands.ItemsSource = Get-CommandObjectsFromText $txtEditor.Text })
$null = $window.ShowDialog()
