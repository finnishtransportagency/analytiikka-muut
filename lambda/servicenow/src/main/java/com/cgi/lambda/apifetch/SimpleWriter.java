package com.cgi.lambda.apifetch;



public interface SimpleWriter {

	public boolean writeDataFile(FileSpec outputFile, String data);

	public FileSpec makeDataFileName(String sourceName, String dataYearMonth);

	
	public boolean writeManifestFile(FileSpec outputFile, String data);

	public FileSpec makeManifestFileName(FileSpec dataFile);
	
}
