package com.example.w6_sqlite;

import android.app.Dialog;
import android.content.pm.PackageManager;
import android.location.Location;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.TextView;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GoogleApiAvailability;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.provider.BaseColumns;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.SimpleCursorAdapter;

import static com.google.android.gms.common.GooglePlayServicesUtil.getErrorDialog;

public class MainActivity extends AppCompatActivity implements
        GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener {

    w6_SQLite mSQLiteExample;
    Button mSQLSubmitButton;
    Cursor mSQLCursor;
    SimpleCursorAdapter mSQLCursorAdapter;
    private static final String TAG = "w6_sql";
    SQLiteDatabase mSQLDB;

    private GoogleApiClient mGoogleApiClient;
    private LocationRequest mLocationRequest;
    private TextView mLatText;
    private TextView mLonText;
    private Location mLastLocation;
    private LocationListener mLocationListener;
    private static final int LOCATION_PERMISSON_RESULT = 17;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sqlite);

        if (mGoogleApiClient == null) {
            mGoogleApiClient = new GoogleApiClient.Builder(this)
                    .addConnectionCallbacks(this)
                    .addOnConnectionFailedListener(this)
                    .addApi(LocationServices.API)
                    .build();
        }
        mLatText = (TextView) findViewById(R.id.lat_output);
        mLonText = (TextView) findViewById(R.id.lon_output);
        mLatText.setText("onCreate Met");
        mLocationRequest = LocationRequest.create();
        mLocationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
        mLocationRequest.setInterval(5000);
        mLocationRequest.setFastestInterval(5000);
        mLocationListener = new LocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                if (location != null) {
                    mLonText.setText(String.valueOf(location.getLongitude()));
                    mLatText.setText(String.valueOf(location.getLatitude()));
                } else {
                    mLonText.setText("No Location Available");
                }
            }
        };


        mSQLiteExample = new w6_SQLite(this);
        mSQLDB = mSQLiteExample.getWritableDatabase();

        mSQLSubmitButton = (Button) findViewById(R.id.sql_add_row_button);
        mSQLSubmitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(mSQLDB != null){
                    ContentValues vals = new ContentValues();
                    vals.put(w6_database_contract.DemoTable.COLUMN_NAME_STRING, ((EditText)findViewById(R.id.sql_text_input)).getText().toString());
                    vals.put(w6_database_contract.DemoTable.COLUMN_NAME_LAT, ((TextView)findViewById(R.id.lat_output)).getText().toString());
                    vals.put(w6_database_contract.DemoTable.COLUMN_NAME_LON, ((TextView)findViewById(R.id.lon_output )).getText().toString());
                    mSQLDB.insert(w6_database_contract.DemoTable.TABLE_NAME,null,vals);
                    populateTable();
                } else {
                    Log.d(TAG, "Unable to access database for writing.");
                }
            }
        });

        populateTable();
    }

    @Override
    protected void onStart() {
        mGoogleApiClient.connect();
        mLatText.setText("Activity Started");
        super.onStart();
    }

    @Override
    protected void onStop() {
        mGoogleApiClient.disconnect();
        super.onStop();
    }

    @Override
    public void onConnected(@Nullable Bundle bundle) {
        mLatText.setText("Ready");
        if (ActivityCompat.checkSelfPermission(this,
                android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION, android.Manifest.permission.ACCESS_COARSE_LOCATION}, LOCATION_PERMISSON_RESULT);
            mLatText.setText("44.5");
            mLonText.setText("-123.2");
            return;
        }
        updateLocation();
    }

    @Override
    public void onConnectionSuspended(int i) {

    }

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {
        Dialog errDialog = GoogleApiAvailability.getInstance().getErrorDialog(this, connectionResult.getErrorCode(), 0);
        errDialog.show();
        return;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults){
        if(requestCode == LOCATION_PERMISSON_RESULT){
            if(grantResults.length > 0){
                updateLocation();
            }
        }
    }

    private void updateLocation() {
        if (ActivityCompat.checkSelfPermission(this,
                android.Manifest.permission.ACCESS_FINE_LOCATION) !=
                PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this,
                android.Manifest.permission.ACCESS_COARSE_LOCATION) !=
                PackageManager.PERMISSION_GRANTED) {
            return;
        }
        LocationServices.FusedLocationApi.requestLocationUpdates(
                mGoogleApiClient,mLocationRequest,mLocationListener);
    }


    private void populateTable(){
        if(mSQLDB != null) {
            try {
                if(mSQLCursorAdapter != null && mSQLCursorAdapter.getCursor() != null){
                    if(!mSQLCursorAdapter.getCursor().isClosed()){
                        mSQLCursorAdapter.getCursor().close();
                    }
                }
                mSQLCursor = mSQLDB.query(w6_database_contract.DemoTable.TABLE_NAME,
                        new String[]{w6_database_contract.DemoTable._ID, w6_database_contract.DemoTable.COLUMN_NAME_STRING,
                                w6_database_contract.DemoTable.COLUMN_NAME_LAT, w6_database_contract.DemoTable.COLUMN_NAME_LON}, w6_database_contract.DemoTable.COLUMN_NAME_LAT + " > ?", new String[]{"0"}, null, null, null);
                ListView SQLListView = (ListView) findViewById(R.id.sql_list_view);
                mSQLCursorAdapter = new SimpleCursorAdapter(this,
                        R.layout.sql_item,
                        mSQLCursor,
                        new String[]{w6_database_contract.DemoTable.COLUMN_NAME_STRING, w6_database_contract.DemoTable.COLUMN_NAME_LAT, w6_database_contract.DemoTable.COLUMN_NAME_LON},
                        new int[]{R.id.sql_listview_string, R.id.sql_listview_lat, R.id.sql_listview_lon},
                        0);
                SQLListView.setAdapter(mSQLCursorAdapter);
            } catch (Exception e) {
                Log.d(TAG, "Error loading data from database");
            }
        }
    }
}

class w6_SQLite extends SQLiteOpenHelper {

    public w6_SQLite(Context context) {
        super(context, w6_database_contract.DemoTable.DB_NAME, null, w6_database_contract.DemoTable.DB_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(w6_database_contract.DemoTable.SQL_CREATE_DEMO_TABLE);


    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL(w6_database_contract.DemoTable.SQL_DROP_DEMO_TABLE);
        onCreate(db);
    }
}

final class w6_database_contract {
    private w6_database_contract(){};

    public final class DemoTable implements BaseColumns {
        public static final String DB_NAME = "demo_db0";
        public static final String TABLE_NAME = "demo0";
        public static final String COLUMN_NAME_STRING = "demo_string";
        public static final String COLUMN_NAME_LAT = "demo_lat";
        public static final String COLUMN_NAME_LON = "demo_long";
        public static final int DB_VERSION = 4;


        public static final String SQL_CREATE_DEMO_TABLE = "CREATE TABLE " +
                DemoTable.TABLE_NAME + "(" + DemoTable._ID + " INTEGER PRIMARY KEY NOT NULL," +
                DemoTable.COLUMN_NAME_STRING + " VARCHAR(255)," +
                DemoTable.COLUMN_NAME_LAT + " VARCHAR(255)," +
                DemoTable.COLUMN_NAME_LON + " VARCHAR(255));";


        public  static final String SQL_DROP_DEMO_TABLE = "DROP TABLE IF EXISTS " + DemoTable.TABLE_NAME;
    }
}